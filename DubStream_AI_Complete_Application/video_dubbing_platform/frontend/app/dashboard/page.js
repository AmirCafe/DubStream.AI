"use client";
import { useEffect, useState } from "react";

export default function DashboardPage() {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) window.location.href = "/login";
    
    fetch(`${process.env.NEXT_PUBLIC_API_BASE}/api/jobs`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    .then(r => r.json())
    .then(d => setJobs(d.jobs || []))
    .finally(() => setLoading(false));
  }, []);

  return (
    <div style={{ padding: "20px", maxWidth: "1200px", margin: "0 auto" }}>
      <h1>Dashboard</h1>
      {loading ? <p>Loading...</p> : jobs.length === 0 ? <p>No videos yet. <a href="/">Upload your first video</a></p> : (
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead><tr style={{ backgroundColor: "#f0f0f0" }}><th style={{ padding: "10px", textAlign: "left", border: "1px solid #ddd" }}>Job ID</th><th style={{ padding: "10px", textAlign: "left", border: "1px solid #ddd" }}>Status</th><th style={{ padding: "10px", textAlign: "left", border: "1px solid #ddd" }}>Progress</th><th style={{ padding: "10px", textAlign: "left", border: "1px solid #ddd" }}>Actions</th></tr></thead>
          <tbody>{jobs.map((job) => (<tr key={job.id} style={{ borderBottom: "1px solid #ddd" }}><td style={{ padding: "10px" }}>{job.id}</td><td style={{ padding: "10px" }}>{job.status}</td><td style={{ padding: "10px" }}>{job.progress}%</td><td style={{ padding: "10px" }}><a href={`/jobs/${job.id}`}>View</a></td></tr>))}</tbody>
        </table>
      )}
    </div>
  );
}
