// Real-Time UPI Fraud Detection - Client Scripts
// Production Security Platform Engine

document.addEventListener("DOMContentLoaded", () => {
    initCharts();
    initSimulator();
    initStreamSimulator();
});

// Global chart references
let riskDoughnutChart = null;
let trendLineChart = null;

function initCharts() {
    const distCanvas = document.getElementById("riskDoughnutChart");
    if (distCanvas && window.Chart) {
        fetch("/api/chart-data")
            .then(res => res.json())
            .then(data => {
                const ctx = distCanvas.getContext("2d");
                riskDoughnutChart = new Chart(ctx, {
                    type: "doughnut",
                    data: {
                        labels: data.distribution.labels,
                        datasets: [{
                            data: data.distribution.counts,
                            backgroundColor: ["#059669", "#d97706", "#ea580c", "#dc2626"],
                            borderWidth: 2,
                            borderColor: "#ffffff"
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: { position: "bottom", labels: { boxWidth: 12, font: { size: 11 } } }
                        },
                        cutout: "68%"
                    }
                });

                const trendCanvas = document.getElementById("trendLineChart");
                if (trendCanvas) {
                    const ctxTrend = trendCanvas.getContext("2d");
                    trendLineChart = new Chart(ctxTrend, {
                        type: "line",
                        data: {
                            labels: data.recent_trend.labels,
                            datasets: [{
                                label: "Hybrid Risk Score",
                                data: data.recent_trend.scores,
                                borderColor: "#1d4ed8",
                                backgroundColor: "rgba(29, 78, 216, 0.08)",
                                fill: true,
                                tension: 0.3,
                                pointBackgroundColor: data.recent_trend.scores.map(s => s >= 90 ? "#dc2626" : (s >= 75 ? "#ea580c" : (s >= 40 ? "#d97706" : "#059669"))),
                                pointRadius: 4
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            scales: {
                                y: { min: 0, max: 100, grid: { color: "#f1f5f9" } },
                                x: { grid: { display: false } }
                            },
                            plugins: {
                                legend: { display: false }
                            }
                        }
                    });
                }
            })
            .catch(err => console.error("Error loading chart data:", err));
    }
}

function initSimulator() {
    const form = document.getElementById("paymentSimForm");
    if (!form) return;

    form.addEventListener("submit", (e) => {
        e.preventDefault();
        runSimulation();
    });

    // Handle user profile selection change
    const userSelect = document.getElementById("user_id");
    if (userSelect) {
        userSelect.addEventListener("change", (e) => {
            const opt = e.target.options[e.target.selectedIndex];
            const avg = opt.getAttribute("data-avg");
            const upi = opt.getAttribute("data-upi");
            if (avg) document.getElementById("user_avg_amount").value = avg;
            if (upi) document.getElementById("sender_upi").value = upi;
        });
    }
}

function setPreset(type) {
    const userSelect = document.getElementById("user_id");
    const opt = userSelect.options[userSelect.selectedIndex];
    const avg = parseFloat(opt.getAttribute("data-avg") || 850);
    
    if (type === "canteen") {
        document.getElementById("amount").value = 140;
        document.getElementById("receiver_upi").value = "canteen.central@upi";
        document.getElementById("hour").value = 13;
        document.getElementById("tx_count_1h").value = 1;
        document.getElementById("tx_count_24h").value = 3;
        document.getElementById("velocity_score").value = 0.10;
        document.getElementById("is_new_device").value = 0;
        document.getElementById("location_change_km").value = 0;
        document.getElementById("ip_risk_score").value = 0.08;
        document.getElementById("is_receiver_flagged").value = 0;
        document.getElementById("failed_pin_attempts").value = 0;
    } else if (type === "rent") {
        document.getElementById("amount").value = Math.round(avg * 4.5);
        document.getElementById("receiver_upi").value = "tatacliq@okhdfcbank";
        document.getElementById("hour").value = 18;
        document.getElementById("tx_count_1h").value = 1;
        document.getElementById("tx_count_24h").value = 2;
        document.getElementById("velocity_score").value = 0.15;
        document.getElementById("is_new_device").value = 0;
        document.getElementById("location_change_km").value = 0;
        document.getElementById("ip_risk_score").value = 0.12;
        document.getElementById("is_receiver_flagged").value = 0;
        document.getElementById("failed_pin_attempts").value = 0;
    } else if (type === "midnight_drain") {
        document.getElementById("amount").value = Math.round(avg * 32.0);
        document.getElementById("receiver_upi").value = "crypto_fastpay_77@axl";
        document.getElementById("hour").value = 3;
        document.getElementById("tx_count_1h").value = 5;
        document.getElementById("tx_count_24h").value = 14;
        document.getElementById("velocity_score").value = 0.88;
        document.getElementById("is_new_device").value = 1;
        document.getElementById("location_change_km").value = 1850;
        document.getElementById("ip_risk_score").value = 0.85;
        document.getElementById("is_receiver_flagged").value = 1;
        document.getElementById("failed_pin_attempts").value = 1;
    } else if (type === "velocity") {
        document.getElementById("amount").value = Math.round(avg * 2.2);
        document.getElementById("receiver_upi").value = "rewards_refund_kfx@sbi";
        document.getElementById("hour").value = 16;
        document.getElementById("tx_count_1h").value = 8;
        document.getElementById("tx_count_24h").value = 22;
        document.getElementById("velocity_score").value = 0.95;
        document.getElementById("is_new_device").value = 0;
        document.getElementById("location_change_km").value = 0;
        document.getElementById("ip_risk_score").value = 0.65;
        document.getElementById("is_receiver_flagged").value = 1;
        document.getElementById("failed_pin_attempts").value = 0;
    } else if (type === "sim_swap") {
        document.getElementById("amount").value = Math.round(avg * 8.5);
        document.getElementById("receiver_upi").value = "unknown_merchant_8819@paytm";
        document.getElementById("hour").value = 23;
        document.getElementById("tx_count_1h").value = 3;
        document.getElementById("tx_count_24h").value = 7;
        document.getElementById("velocity_score").value = 0.62;
        document.getElementById("is_new_device").value = 1;
        document.getElementById("location_change_km").value = 950;
        document.getElementById("ip_risk_score").value = 0.72;
        document.getElementById("is_receiver_flagged").value = 1;
        document.getElementById("failed_pin_attempts").value = 2;
    }

    runSimulation();
}

function runSimulation() {
    const payload = {
        user_id: document.getElementById("user_id").value,
        sender_upi: document.getElementById("sender_upi").value,
        receiver_upi: document.getElementById("receiver_upi").value,
        amount: parseFloat(document.getElementById("amount").value),
        user_avg_amount: parseFloat(document.getElementById("user_avg_amount").value),
        hour: parseInt(document.getElementById("hour").value),
        tx_count_1h: parseInt(document.getElementById("tx_count_1h").value),
        tx_count_24h: parseInt(document.getElementById("tx_count_24h").value),
        velocity_score: parseFloat(document.getElementById("velocity_score").value),
        is_new_device: parseInt(document.getElementById("is_new_device").value),
        location_change_km: parseFloat(document.getElementById("location_change_km").value),
        ip_risk_score: parseFloat(document.getElementById("ip_risk_score").value),
        is_receiver_flagged: parseInt(document.getElementById("is_receiver_flagged").value),
        failed_pin_attempts: parseInt(document.getElementById("failed_pin_attempts").value)
    };

    const submitBtn = document.getElementById("submitSimBtn");
    if (submitBtn) submitBtn.innerText = "Analyzing Behavioral Signatures...";

    fetch("/api/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    })
    .then(r => r.json())
    .then(data => {
        if (submitBtn) submitBtn.innerText = "Authorize & Scan Transaction";
        if (!data.success) throw new Error(data.error || "Transaction failed");
        displayResult(data.transaction);
    })
    .catch(err => {
        if (submitBtn) submitBtn.innerText = "Authorize & Scan Transaction";
        alert(err.message);
        console.error("Simulation error:", err);
    });
}

function displayResult(tx) {
    const resultCard = document.getElementById("simResultCard");
    if (!resultCard) return;

    resultCard.style.display = "block";
    resultCard.className = `result-card status-${tx.badge_class}`;

    // Fill elements
    document.getElementById("resScore").innerText = tx.risk_score;
    document.getElementById("resStatus").className = `badge-status ${tx.badge_class}`;
    document.getElementById("resStatus").innerHTML = `<span class="dot-indicator"></span> ${tx.status}`;
    document.getElementById("resAction").innerText = tx.action;
    document.getElementById("resRecommendation").innerText = tx.recommendation;

    // Meter bar
    const meterFill = document.getElementById("resMeterFill");
    meterFill.style.width = `${Math.max(4, tx.risk_score)}%`;
    meterFill.className = `risk-meter-fill ${tx.badge_class}`;

    // Model breakdown
    document.getElementById("resXgb").innerText = `${tx.models.xgboost_prob}%`;
    document.getElementById("resRf").innerText = `${tx.models.random_forest_prob}%`;
    document.getElementById("resIso").innerText = `${tx.models.isolation_forest_anomaly}%`;

    // Explainable AI reasons list
    const reasonsContainer = document.getElementById("resReasonsList");
    reasonsContainer.innerHTML = "";
    
    const reasons = tx.explanations.key_reasons || [];
    if (reasons.length === 0) {
        reasonsContainer.innerHTML = `<li class="xai-reason-item safe">All behavioral indicators conform to normal baseline profile.</li>`;
    } else {
        reasons.forEach(r => {
            const li = document.createElement("li");
            li.className = `xai-reason-item ${tx.badge_class === "safe" ? "safe" : "risk"}`;
            li.innerHTML = `<strong>${tx.badge_class === "safe" ? "✓" : "⚠"}</strong> <span>${r}</span>`;
            reasonsContainer.appendChild(li);
        });
    }

    // Factors table
    const factorsContainer = document.getElementById("resFactorsList");
    if (factorsContainer && tx.explanations.factors) {
        factorsContainer.innerHTML = "";
        tx.explanations.factors.forEach(f => {
            const div = document.createElement("div");
            div.style.display = "flex";
            div.style.justifyContent = "space-between";
            div.style.padding = "4px 0";
            div.style.fontSize = "0.8rem";
            div.style.borderBottom = "1px dashed #e2e8f0";
            div.innerHTML = `
                <span>${f.feature} <small style="color:#64748b">(${f.desc})</small></span>
                <span style="font-weight:600; color:${f.direction === 'risk' ? '#dc2626' : '#059669'}">
                    ${f.direction === 'risk' ? '+' : '-'}${f.weight}
                </span>
            `;
            factorsContainer.appendChild(div);
        });
    }

    renderPaymentControls(tx);
    resultCard.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

function initStreamSimulator() {
    const streamBtn = document.getElementById("btnSimStream");
    if (!streamBtn) return;

    streamBtn.addEventListener("click", () => {
        streamBtn.disabled = true;
        streamBtn.innerHTML = `<span class="pulse-dot"></span> Generating Live Traffic...`;

        fetch("/api/simulate-stream", { method: "POST" })
            .then(r => r.json())
            .then(data => {
                streamBtn.disabled = false;
                streamBtn.innerHTML = `⚡ Generate Live Transaction`;
                
                // Prepend to dashboard table if present
                const tbody = document.getElementById("liveTxTableBody");
                if (tbody && data.transaction) {
                    const tx = data.transaction;
                    const row = document.createElement("tr");
                    row.style.backgroundColor = "#eff6ff";
                    row.innerHTML = `
                        <td class="mono">${tx.transaction_id}</td>
                        <td>${tx.timestamp.split(" ")[1]}</td>
                        <td><strong>${tx.sender_upi}</strong></td>
                        <td>${tx.receiver_upi}</td>
                        <td style="font-weight:700">₹${Number(tx.amount).toLocaleString('en-IN', {minimumFractionDigits: 2})}</td>
                        <td><strong>${tx.risk_score}</strong> / 100</td>
                        <td><span class="badge-status ${tx.badge_class}"><span class="dot-indicator"></span>${tx.status}</span></td>
                        <td><small style="color:#64748b">${tx.action}</small></td>
                    `;
                    tbody.insertBefore(row, tbody.firstChild);
                    setTimeout(() => { row.style.backgroundColor = ""; }, 2000);
                }
            })
            .catch(err => {
                streamBtn.disabled = false;
                streamBtn.innerHTML = `⚡ Generate Live Transaction`;
                console.error("Stream error:", err);
            });
    });
}

let holdTimer;
function renderPaymentControls(tx) {
    clearInterval(holdTimer);
    const controls=document.getElementById("holdControls");
    document.getElementById("resReputation").textContent=tx.receiver_reputation.score+"/100 — "+tx.receiver_reputation.category;
    document.getElementById("resBalances").textContent="Demo balances: sender ₹"+tx.sender_balance+" | receiver ₹"+tx.receiver_balance;
    document.getElementById("resPaymentState").textContent=tx.state+" — "+(tx.money_transferred?"Simulated money transferred":"No money transferred");
    controls.hidden=tx.state!=="Held";
    if(controls.hidden) return;
    const verify=document.getElementById("demoVerification");
    verify.hidden=tx.status!=="High Risk";
    document.getElementById("demoCode").textContent=tx.demo_code||"";
    document.getElementById("verificationCode").value="";
    const countdown=document.getElementById("holdCountdown");
    const deadline=Date.now()+1000*tx.expires_in;
    const tick=()=>{const n=Math.max(0,Math.ceil((deadline-Date.now())/1000));
        countdown.textContent=n+" seconds remaining";
        if(n===0){clearInterval(holdTimer);controls.hidden=true;
            document.getElementById("resPaymentState").textContent="Expired — No money transferred";}};
    tick();holdTimer=setInterval(tick,250);
    async function decidePayment(decision){
        const buttons=[document.getElementById("proceedPayment"),document.getElementById("cancelPayment")];
        buttons.forEach(b=>b.disabled=true);
        try{
            const r=await fetch("/api/transactions/"+encodeURIComponent(tx.transaction_id)+"/decision",{
                method:"POST",headers:{"Content-Type":"application/json"},
                body:JSON.stringify({decision,code:document.getElementById("verificationCode").value})});
            const data=await r.json();
            if(!data.success)throw new Error(data.error);
            displayResult(data.transaction);
        }catch(e){alert(e.message);}finally{buttons.forEach(b=>b.disabled=false);}
    }
    document.getElementById("proceedPayment").onclick=()=>decidePayment("proceed");
    document.getElementById("cancelPayment").onclick=()=>decidePayment("cancel");
}
