import { useState, useEffect } from "react";
import "./styles.css";

export default function App() {
  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || "/api";

  const [view, setView] = useState("login"); // login | signup | todos
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("user");

  const [loginUsername, setLoginUsername] = useState("");
  const [loginPassword, setLoginPassword] = useState("");

  const [todos, setTodos] = useState([]);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");

  const [token, setToken] = useState(localStorage.getItem("token") || null);
  const [loggedIn, setLoggedIn] = useState(!!localStorage.getItem("token"));
  const [currentUser, setCurrentUser] = useState("");

  const [editingId, setEditingId] = useState(null);
  const [editTitle, setEditTitle] = useState("");
  const [editDescription, setEditDescription] = useState("");

  // ----------------- Signup -----------------
  const handleSignup = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch(`${BACKEND_URL}/users`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, email, username, password, role }),
      });

      if (!res.ok) {
        const errorData = await res.json();
        alert("Signup failed: " + JSON.stringify(errorData));
        return;
      }

      alert("Signup successful! Please login.");
      setView("login");
    } catch (err) {
      alert("Signup failed: " + err.message);
    }
  };

  // ----------------- Login -----------------
  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch(`${BACKEND_URL}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams({
          username: loginUsername,
          password: loginPassword,
        }),
      });

      if (!res.ok) {
        const errorData = await res.json();
        alert("Login failed: " + JSON.stringify(errorData));
        return;
      }

      const data = await res.json();
      localStorage.setItem("token", data.access_token);
      setToken(data.access_token);
      setLoggedIn(true);
      setView("todos");
      fetchUser(data.access_token);
    } catch (err) {
      alert("Login failed: " + err.message);
    }
  };

  // ----------------- Fetch Todos -----------------
  const fetchTodos = async () => {
    if (!token) return;
    try {
      const res = await fetch(`${BACKEND_URL}/todos`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await res.json();
      setTodos(data);
    } catch (err) {
      console.error(err);
    }
  };

  // ----------------- Fetch Current User -----------------
  const fetchUser = async (tk = token) => {
    if (!tk) return;
    try {
      const res = await fetch(`${BACKEND_URL}/me`, {
        headers: { Authorization: `Bearer ${tk}` },
      });
      if (res.ok) {
        const data = await res.json();
        setCurrentUser(data.username);
      }
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    if (loggedIn && token) {
      fetchTodos();
      fetchUser(token);
    }
  }, [loggedIn, token]);

  // ----------------- Add Todo -----------------
  const addTodo = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch(`${BACKEND_URL}/todos`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ title, description }),
      });

      if (!res.ok) throw new Error("Failed to add todo");
      await fetchTodos();
      setTitle("");
      setDescription("");
    } catch (err) {
      alert(err.message);
    }
  };

  // ----------------- Toggle Todo -----------------
  const toggleTodo = async (id, completed) => {
    try {
      const res = await fetch(`${BACKEND_URL}/todos/${id}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ completed: !completed }),
      });
      if (!res.ok) throw new Error("Failed to toggle todo");
      await fetchTodos();
    } catch (err) {
      alert(err.message);
    }
  };

  // ----------------- Delete Todo -----------------
  const deleteTodo = async (id) => {
    try {
      const res = await fetch(`${BACKEND_URL}/todos/${id}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) throw new Error("Failed to delete todo");
      await fetchTodos();
    } catch (err) {
      alert(err.message);
    }
  };

  // ----------------- Update Todo -----------------
  const updateTodo = async (id) => {
    try {
      const res = await fetch(`${BACKEND_URL}/todos/${id}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          title: editTitle,
          description: editDescription,
        }),
      });
      if (!res.ok) throw new Error("Failed to update todo");
      setEditingId(null);
      setEditTitle("");
      setEditDescription("");
      await fetchTodos();
    } catch (err) {
      alert(err.message);
    }
  };

  // ----------------- Cancel Edit -----------------
  const cancelEdit = () => {
    setEditingId(null);
    setEditTitle("");
    setEditDescription("");
  };

  // ----------------- Logout -----------------
  const handleLogout = () => {
    localStorage.removeItem("token");
    setToken(null);
    setLoggedIn(false);
    setView("login");
    setCurrentUser("");
  };

  return (
    <div className="container">
      {/* -------- Signup -------- */}
      {view === "signup" && (
        <>
          <h2>Signup</h2>
          <form onSubmit={handleSignup}>
            <input
              type="text"
              placeholder="Full Name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
            <input
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
            <input
              type="text"
              placeholder="Username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
            <select value={role} onChange={(e) => setRole(e.target.value)}>
              <option value="user">User</option>
              <option value="admin">Admin</option>
            </select>
            <button type="submit">Signup</button>
          </form>
          <p>
            Already have an account?{" "}
            <span className="link" onClick={() => setView("login")}>
              Login
            </span>
          </p>
        </>
      )}

      {/* -------- Login -------- */}
      {view === "login" && (
        <>
          <h2>Login</h2>
          <form onSubmit={handleLogin}>
            <input
              type="text"
              placeholder="Username"
              value={loginUsername}
              onChange={(e) => setLoginUsername(e.target.value)}
              required
            />
            <input
              type="password"
              placeholder="Password"
              value={loginPassword}
              onChange={(e) => setLoginPassword(e.target.value)}
              required
            />
            <button type="submit">Login</button>
          </form>
          <p>
            Don't have an account?{" "}
            <span className="link" onClick={() => setView("signup")}>
              Signup
            </span>
          </p>
        </>
      )}

      {/* -------- Todos -------- */}
      {view === "todos" && (
        <>
          <h2>My Todos</h2>
          {currentUser && (
            <p>
              Welcome, <b>{currentUser}</b> 👋
            </p>
          )}

          <form onSubmit={addTodo} className="todo-form">
            <input
              type="text"
              placeholder="Title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
            />
            <input
              type="text"
              placeholder="Description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              required
            />
            <button type="submit">Add Todo</button>
          </form>

          <table>
            <thead>
              <tr>
                <th>Done</th>
                <th>Title</th>
                <th>Description</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {todos.map((todo) => (
                <tr key={todo.id} className={todo.completed ? "done" : ""}>
                  <td>
                    <input
                      type="checkbox"
                      checked={todo.completed}
                      onChange={() => toggleTodo(todo.id, todo.completed)}
                    />
                  </td>
                  <td>
                    {editingId === todo.id ? (
                      <input
                        value={editTitle}
                        onChange={(e) => setEditTitle(e.target.value)}
                      />
                    ) : (
                      todo.title
                    )}
                  </td>
                  <td>
                    {editingId === todo.id ? (
                      <input
                        value={editDescription}
                        onChange={(e) => setEditDescription(e.target.value)}
                      />
                    ) : (
                      todo.description
                    )}
                  </td>
                  <td>
                    {editingId === todo.id ? (
                      <>
                        <button onClick={() => updateTodo(todo.id)}>
                          Save
                        </button>
                        <button onClick={cancelEdit}>Cancel</button>
                      </>
                    ) : (
                      <>
                        <button
                          onClick={() => {
                            setEditingId(todo.id);
                            setEditTitle(todo.title);
                            setEditDescription(todo.description);
                          }}
                        >
                          Edit
                        </button>
                        <button onClick={() => deleteTodo(todo.id)}>
                          Delete
                        </button>
                      </>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          <button onClick={handleLogout} className="logout-btn">
            Logout
          </button>
        </>
      )}
    </div>
  );
}
