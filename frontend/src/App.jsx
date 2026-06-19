import { useState } from "react";
import { validateFile, downloadUrl } from "./api";

export default function App() {
	const [file, setFile] = useState(null);
	const [dragging, setDragging] = useState(false);
	const [chunkSize, setChunkSize] = useState(500);
	const [result, setResult] = useState(null);
	const [loading, setLoading] = useState(false);
	const [error, setError] = useState("");

	async function handleValidate() {
		if (!file) return;
		setLoading(true);
		setError("");
		setResult(null);
		try {
			const data = await validateFile(file);
			setResult(data);
		} catch {
			setError("Could not validate the file. Is the backend running?");
		} finally {
			setLoading(false);
		}
	}

	return (
		<div className="container">
			<h1>Transaction Data Validator</h1>
			<p className="sub">
				Upload a transactions CSV to check phone numbers, dates, amounts and
				payment modes. Valid rows can be downloaded as a cleaned file or split
				into chunks.
			</p>

			<div className="box">
				<label
					className={`dropzone ${dragging ? "dragging" : ""}`}
					onDragOver={(e) => {
						e.preventDefault();
						setDragging(true);
					}}
					onDragLeave={() => setDragging(false)}
					onDrop={(e) => {
						e.preventDefault();
						setDragging(false);
						setFile(e.dataTransfer.files[0]);
					}}
				>
					<input
						type="file"
						accept=".csv,.xlsx"
						onChange={(e) => setFile(e.target.files[0])}
						hidden
					/>
					<svg
						className="dropzone-icon"
						viewBox="0 0 24 24"
						fill="none"
						stroke="currentColor"
						strokeWidth="1.8"
						strokeLinecap="round"
						strokeLinejoin="round"
					>
						<path d="M12 16V4m0 0L7 9m5-5l5 5" />
						<path d="M4 20h16" />
					</svg>
					{file ? (
						<p className="dropzone-file">{file.name}</p>
					) : (
						<p className="dropzone-text">
							<strong>Click to upload</strong> or drag and drop
						</p>
					)}
					<p className="dropzone-sub">CSV or Excel file</p>
				</label>
				<label className="chunk">
					Chunk size:
					<input
						type="number"
						min="1"
						value={chunkSize}
						onChange={(e) => setChunkSize(Number(e.target.value))}
					/>
				</label>
				<button onClick={handleValidate} disabled={!file || loading}>
					{loading ? "Validating..." : "Validate"}
				</button>
				<p className="hint">Supported countries: IN, SG, US, UK, AE</p>
			</div>

			{error && <p className="error">{error}</p>}

			{result && (
				<div className="box">
					<div className="stats">
						<span>
							Total: <b>{result.summary.total}</b>
						</span>
						<span className="ok">
							Valid: <b>{result.summary.valid}</b>
						</span>
						<span className="bad">
							Invalid: <b>{result.summary.invalid}</b>
						</span>
					</div>

					<div className="downloads">
						<a href={downloadUrl(result.job_id, "cleaned")}>Cleaned CSV</a>
						<a href={downloadUrl(result.job_id, "errors")}>Error report</a>
						<a href={downloadUrl(result.job_id, "chunks", chunkSize)}>
							Chunks (zip)
						</a>
					</div>

					{result.errors.length > 0 ? (
						<table>
							<thead>
								<tr>
									<th>Row</th>
									<th>Order ID</th>
									<th>Problem</th>
								</tr>
							</thead>
							<tbody>
								{result.errors.map((e, i) => (
									<tr key={i}>
										<td>{e.row}</td>
										<td>{e.order_id}</td>
										<td>{e.problem}</td>
									</tr>
								))}
							</tbody>
						</table>
					) : (
						<p className="ok">All rows passed validation.</p>
					)}
				</div>
			)}
		</div>
	);
}
