document.addEventListener("DOMContentLoaded", () => {
    fetch("/api/wallet")
        .then(res => res.json())
        .then(wallet => {
            const div = document.getElementById("wallet-stats");
            div.innerHTML = `
                <p>USD: $${wallet.usd_balance.toFixed(2)}</p>
                <p>Balances:</p>
                <ul>${Object.entries(wallet.balances).map(
                    ([coin, amt]) => `<li>${coin.toUpperCase()}: ${amt.toFixed(6)}</li>`
                ).join("")}</ul>
            `;
        });

    fetch("/api/trade-history")
        .then(res => res.json())
        .then(trades => {
            const list = document.getElementById("trade-list");
            list.innerHTML = trades.slice(-10).reverse().map(t => `
                <li>${t.timestamp || 'N/A'} — ${t.action.toUpperCase()} ${t.amount} @ $${t.price}</li>
            `).join("");
        });

    fetch("/api/logs")
        .then(res => res.json())
        .then(logs => {
            const list = document.getElementById("pattern-log");
            list.innerHTML = logs.reverse().map(entry => `
                <li>${entry.timestamp} — ${entry.coin.toUpperCase()} | RSI: ${entry.rsi} | ${entry.trade_action}</li>
            `).join("");
        });

    // Chat box handling
    document.getElementById("chat-form").addEventListener("submit", async e => {
        e.preventDefault();
        const input = document.getElementById("user_input");
        const message = input.value;
        input.value = "";

        const res = await fetch("/chat", {
            method: "POST",
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_input: message })
        });

        const data = await res.json();
        const chatBox = document.getElementById("chat-box");
        chatBox.innerHTML += `<p><strong>You:</strong> ${message}</p>`;
        chatBox.innerHTML += `<p><strong>Nikki:</strong> ${data.response}</p>`;
        chatBox.scrollTop = chatBox.scrollHeight;
    });
});
