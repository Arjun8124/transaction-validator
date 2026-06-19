import axios from "axios";

const API = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000";

export async function validateFile(file) {
	const form = new FormData();
	form.append("file", file);
	const { data } = await axios.post(`${API}/api/validate`, form);
	return data;
}

export function downloadUrl(jobId, kind, size) {
	const query = kind === "chunks" && size ? `?size=${size}` : "";
	return `${API}/api/download/${jobId}/${kind}${query}`;
}
