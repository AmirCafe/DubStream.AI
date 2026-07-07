"use client";
import { useState } from "react";

export default function RegisterPage() {
  const [formData, setFormData] = useState({ email: "", password: "", full_name: "" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleRegister = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE}/api/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });
      if (!response.ok) throw new Error("Registration failed");
      window.location.href = "/login";
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: "400px", margin: "100px auto", padding: "20px" }}>
      <h1>Create Account</h1>
      {error && <p style={{ color: "red" }}>{error}</p>}
      <form onSubmit={handleRegister}>
        <div style={{ marginBottom: "15px" }}>
          <input type="text" placeholder="Full Name" value={formData.full_name} onChange={(e) => setFormData({ ...formData, full_name: e.target.value })} style={{ width: "100%", padding: "10px", fontSize: "16px" }} required />
        </div>
        <div style={{ marginBottom: "15px" }}>
          <input type="email" placeholder="Email" value={formData.email} onChange={(e) => setFormData({ ...formData, email: e.target.value })} style={{ width: "100%", padding: "10px", fontSize: "16px" }} required />
        </div>
        <div style={{ marginBottom: "15px" }}>
          <input type="password" placeholder="Password" value={formData.password} onChange={(e) => setFormData({ ...formData, password: e.target.value })} style={{ width: "100%", padding: "10px", fontSize: "16px" }} required />
        </div>
        <button type="submit" disabled={loading} style={{ width: "100%", padding: "10px", fontSize: "16px", backgroundColor: "#28a745", color: "white", border: "none", borderRadius: "4px", cursor: "pointer" }}>
          {loading ? "Creating..." : "Create Account"}
        </button>
      </form>
      <p style={{ textAlign: "center", marginTop: "20px" }}>Already have an account? <a href="/login">Sign in</a></p>
    </div>
  );
}
