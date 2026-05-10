// ─────────────────────────────────────────────────────────────
// CONFIG
// ─────────────────────────────────────────────────────────────
const BASE_URL      = "http://127.0.0.1:5000";
const OTP_EXPIRY_S  = 120;   // Must match backend OTP_EXPIRY_SECONDS

// ─────────────────────────────────────────────────────────────
// ELEMENTS
// ─────────────────────────────────────────────────────────────
const userInput   = document.getElementById("user_id");
const generateBtn = document.getElementById("generate-btn");
const verifyBtn   = document.getElementById("verify-btn");
const otpInputs   = document.querySelectorAll(".otp-box");
const statusBox   = document.getElementById("status-msg");
const timerCount  = document.getElementById("timer-count");
const timerLabel  = document.getElementById("timer-label");
const logContainer= document.getElementById("audit-log");
const svgCircle   = document.getElementById("progress-circle");

const OTP_LENGTH   = otpInputs.length;   // driven by HTML, stays in sync
const CIRCUMFERENCE = 2 * Math.PI * 34;  // r=34 matches SVG

// ─────────────────────────────────────────────────────────────
// STATE
// ─────────────────────────────────────────────────────────────
let currentUser    = null;
let timerInterval  = null;
let otpActive      = false;

// ─────────────────────────────────────────────────────────────
// AUDIT LOG
// ─────────────────────────────────────────────────────────────
function log(tag, msg, level = "info") {
    const colors = { info: "text-primary/40", auth: "text-secondary/40", err: "text-red-400/60", ok: "text-green-400/60" };
    const color  = colors[level] || colors.info;
    const line   = document.createElement("p");
    line.innerHTML = `<span class="${color}">[${tag.toUpperCase()}]</span> ${msg}`;
    logContainer.appendChild(line);
    logContainer.scrollTop = logContainer.scrollHeight;
}

// ─────────────────────────────────────────────────────────────
// STATUS MESSAGE (replaces alert())
// ─────────────────────────────────────────────────────────────
function showStatus(msg, type = "info") {
    statusBox.textContent = msg;
    statusBox.className = "status-msg status-" + type;
    statusBox.classList.remove("hidden");
    clearTimeout(showStatus._timeout);
    showStatus._timeout = setTimeout(() => statusBox.classList.add("hidden"), 5000);
}

// ─────────────────────────────────────────────────────────────
// OTP INPUT — AUTO ADVANCE & BACKSPACE
// ─────────────────────────────────────────────────────────────
otpInputs.forEach((input, index) => {
    input.addEventListener("input", () => {
        // Strip non-digits
        input.value = input.value.replace(/\D/g, "").slice(-1);
        if (input.value && index < otpInputs.length - 1) {
            otpInputs[index + 1].focus();
        }
    });

    input.addEventListener("keydown", (e) => {
        if (e.key === "Backspace" && !input.value && index > 0) {
            otpInputs[index - 1].focus();
        }
    });

    // Prevent paste of multiple chars from flooding one box
    input.addEventListener("paste", (e) => {
        e.preventDefault();
        const pasted = (e.clipboardData || window.clipboardData)
            .getData("text")
            .replace(/\D/g, "")
            .slice(0, OTP_LENGTH);
        [...pasted].forEach((char, i) => {
            if (otpInputs[i]) otpInputs[i].value = char;
        });
        const next = Math.min(pasted.length, OTP_LENGTH - 1);
        otpInputs[next].focus();
    });
});

function getOtp() {
    return Array.from(otpInputs).map(i => i.value).join("");
}

function clearOtpInputs() {
    otpInputs.forEach(i => { i.value = ""; });
    otpInputs[0].focus();
}

// ─────────────────────────────────────────────────────────────
// CIRCULAR TIMER
// ─────────────────────────────────────────────────────────────
function startTimer(seconds) {
    clearInterval(timerInterval);
    otpActive = true;

    let remaining = seconds;

    function tick() {
        timerCount.textContent = remaining;

        // Update SVG progress ring
        if (svgCircle) {
            const offset = CIRCUMFERENCE * (1 - remaining / seconds);
            svgCircle.style.strokeDashoffset = offset;
        }

        if (remaining <= 0) {
            clearInterval(timerInterval);
            otpActive = false;
            showStatus("OTP expired. Please generate a new one.", "error");
            log("SYS", "OTP token expired", "err");
            timerCount.textContent = "0";
            clearOtpInputs();
        }

        remaining--;
    }

    tick();
    timerInterval = setInterval(tick, 1000);
}

function stopTimer() {
    clearInterval(timerInterval);
    otpActive = false;
    timerCount.textContent = "--";
    if (svgCircle) svgCircle.style.strokeDashoffset = 0;
}

// ─────────────────────────────────────────────────────────────
// LOADING STATE
// ─────────────────────────────────────────────────────────────
function setLoading(btn, state) {
    btn.disabled = state;
    btn.classList.toggle("opacity-60", state);
    btn.classList.toggle("cursor-not-allowed", state);
}

// ─────────────────────────────────────────────────────────────
// GENERATE OTP
// ─────────────────────────────────────────────────────────────
generateBtn.addEventListener("click", async () => {
    const user_id = userInput.value.trim();

    if (!user_id) {
        showStatus("Please enter a User ID.", "error");
        userInput.focus();
        return;
    }

    if (!/^[A-Za-z0-9_\-]{1,64}$/.test(user_id)) {
        showStatus("User ID may only contain letters, numbers, _ or - (max 64 chars).", "error");
        return;
    }

    setLoading(generateBtn, true);
    log("AUTH", `Requesting OTP for user: ${user_id}`);

    try {
        const res = await fetch(`${BASE_URL}/generate-otp`, {
            method:  "POST",
            headers: { "Content-Type": "application/json" },
            body:    JSON.stringify({ user_id }),
        });

        const data = await res.json();

        if (!res.ok) {
            const msg = data.error || "Failed to generate OTP.";
            showStatus(msg, "error");
            log("ERR", msg, "err");
            return;
        }

        currentUser = user_id;
        clearOtpInputs();
        stopTimer();
        startTimer(OTP_EXPIRY_S);

        showStatus("OTP sent! Check your registered channel.", "success");
        log("AUTH", "OTP generated and dispatched", "ok");
        log("SYS", `Token valid for ${OTP_EXPIRY_S}s`, "info");

    } catch {
        showStatus("Cannot connect to server. Is the backend running?", "error");
        log("ERR", "Network error — server unreachable", "err");
    } finally {
        setLoading(generateBtn, false);
    }
});

// ─────────────────────────────────────────────────────────────
// VERIFY OTP
// ─────────────────────────────────────────────────────────────
verifyBtn.addEventListener("click", async () => {
    if (!currentUser) {
        showStatus("Generate an OTP first.", "error");
        return;
    }

    const otp = getOtp();

    if (otp.length !== OTP_LENGTH) {
        showStatus(`Enter all ${OTP_LENGTH} digits of the OTP.`, "error");
        return;
    }

    setLoading(verifyBtn, true);
    log("AUTH", "Submitting verification token...");

    try {
        const res = await fetch(`${BASE_URL}/verify-otp`, {
            method:  "POST",
            headers: { "Content-Type": "application/json" },
            body:    JSON.stringify({ user_id: currentUser, otp }),
        });

        const data = await res.json();

        if (res.ok) {
            stopTimer();
            showStatus("✅ Access Granted!", "success");
            log("AUTH", "Verification successful — access granted", "ok");
            clearOtpInputs();
            currentUser = null;
        } else {
            const msg = data.error || "Verification failed.";
            showStatus(msg, "error");
            log("AUTH", `Verification failed: ${msg}`, "err");

            // Clear inputs on lockout or expiry
            if (res.status === 429 || res.status === 410) {
                stopTimer();
                clearOtpInputs();
                currentUser = null;
            }
        }

    } catch {
        showStatus("Server error during verification.", "error");
        log("ERR", "Network error during verify", "err");
    } finally {
        setLoading(verifyBtn, false);
    }
});

// ─────────────────────────────────────────────────────────────
// INITIAL LOG
// ─────────────────────────────────────────────────────────────
log("INFO", "Initializing BBS Core...");
log("INFO", "Blum Blum Shub CSPRNG ready");
log("AUTH", "Waiting for User ID entry");
log("SYS",  "Vault connection established");
