import { useState } from "react";
const API = "http://localhost:8002";
const threadId = crypto.randomUUID();

export default function App() {
  const [msgs, setMsgs] = useState([]);
  const [text, setText] = useState("");
  const [pending, setPending] = useState(null);
  const [busy, setBusy] = useState(false);

  async function call(path, body) {
    setBusy(true);
    const res = await fetch(API + path, {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ thread_id: threadId, ...body }),
    });
    const data = await res.json();
    setBusy(false);
    if (data.pending_approval) setPending(data.pending_approval);
    else { setPending(null); setMsgs(m => [...m, { role: "agent", text: data.reply }]); }
  }

  function send() {
    if (!text.trim()) return;
    setMsgs(m => [...m, { role: "user", text }]);
    call("/chat", { message: text });
    setText("");
  }

  return (
    <div style={{ maxWidth: 600, margin: "40px auto", fontFamily: "sans-serif" }}>
      <h2>Support Agent</h2>
      {msgs.map((m, i) => (
        <p key={i} style={{ textAlign: m.role === "user" ? "right" : "left" }}>
          <b>{m.role === "user" ? "You" : "Agent"}:</b> {m.text}
        </p>
      ))}
      {busy && <p>Thinking...</p>}
      {pending && (
        <div style={{ border: "1px solid orange", padding: 10 }}>
          Agent wants to run {pending.map(c => `${c.name}(${JSON.stringify(c.args)})`).join(", ")}
          <br />
          <button onClick={() => call("/approve", { approve: true })}>Approve</button>
          <button onClick={() => call("/approve", { approve: false })}>Reject</button>
        </div>
      )}
      <input value={text} onChange={e => setText(e.target.value)}
             onKeyDown={e => e.key === "Enter" && send()} style={{ width: "80%" }} />
      <button onClick={send} disabled={busy}>Send</button>
    </div>
  );
}
