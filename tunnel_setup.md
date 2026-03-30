# CodeAtlas Local Tunnel Setup (Free Tier)

This guide will show you how to connect your **Render** website precisely to your **Mac's Ollama** so you can use the platform for $0/month.

### **Step 1: Install ngrok**
If you don't have ngrok, open your terminal and run:
```bash
brew install ngrok/ngrok/ngrok
```
*(Or download it from [ngrok.com](https://ngrok.com/download))*

### **Step 2: Start the Tunnel**
In a new terminal tab, run this command to expose your Ollama port:
```bash
ngrok http 11434
```

### **Step 3: Get your Public URL**
Once ngrok starts, look for the **Forwarding** line. It will look like this:
`Forwarding  https://a1b2-c3d4.ngrok-free.app -> http://localhost:11434`

**Copy the `https://...` URL.**

### **Step 4: Update Render**
1.  Go to your **Render Dashboard**.
2.  Select your `codeatlas-backend` service.
3.  Go to **Environment**.
4.  Update the `OLLAMA_URL` variable with the URL you copied in Step 3.
5.  **Save Changes**.

---

### **⚠️ Important Notes:**
- **Keep it Open**: Your website will only work while the `ngrok` command is running in your terminal.
- **Privacy**: ngrok creates a secure tunnel. Only your Render backend will know this URL if you keep it private.
- **Sleep Mode**: If your Mac goes to sleep, the tunnel will disconnect. 
