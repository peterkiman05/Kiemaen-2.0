export interface ChatPayload { session_id: string; message: string; }
export interface ChatResponse { agent: string; session_id: string; supervisor_route: string; reply: string; execution_output: string; model_used: string; }

export const sendChatMessage = async (payload: ChatPayload): Promise<ChatResponse> => {
  const res = await fetch("/chat", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
  if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
  return res.json();
};
