// 🕰️ Auto-refresh stats every 10 seconds
function updateStats() {
    fetch("/stats")
      .then(res => res.json())
      .then(data => {
        document.getElementById("usdBalance").textContent = `$${data.wallet.usd_balance.toFixed(2)}`;
        document.getElementById("btcBalance").textContent = `${(data.wallet.balances.bitcoin || 0).toFixed(6)} BTC`;
        document.getElementById("lastUpdated").textContent = `⏱️ Last synced: ${data.timestamp}`;
      });
  }
  
  setInterval(updateStats, 10000);
  updateStats();
  
  // 💬 Nikki Chat Logic
  const chatForm = document.getElementById("chat-form");
  const chatInput = document.getElementById("chat-input");
  const chatLog = document.getElementById("chat-log");
  
  chatForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const userMsg = chatInput.value.trim();
    if (!userMsg) return;
  
    appendToChat("You", userMsg);
    chatInput.value = "";
  
    const response = await fetch("/chat", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ message: userMsg })
    });
  
    const data = await response.json();
    appendToChat("Nikki", data.response);
  });
  
  function appendToChat(sender, message) {
    const bubble = document.createElement("div");
    bubble.classList.add("chat-bubble", sender === "Nikki" ? "nikki" : "user");
    bubble.textContent = `${sender}: ${message}`;
    chatLog.appendChild(bubble);
    chatLog.scrollTop = chatLog.scrollHeight;
  }
  