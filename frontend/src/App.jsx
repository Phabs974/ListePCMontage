import React, { useEffect, useMemo, useState } from "react";
import {
  createOrder,
  createUser,
  deleteOrder,
  deleteUser,
  getMe,
  importInvoice,
  listOrders,
  listUsers,
  login,
  setToken,
  updateOrder,
  updateUser,
} from "./api.js";

const views = [
  { key: "all", label: "Tous" },
  { key: "to_prepare", label: "À préparer" },
  { key: "to_build", label: "À monter" },
  { key: "to_deliver", label: "À livrer" },
  { key: "done", label: "Terminé" },
];

function formatDateTime(value) {
  const date = new Date(value);
  return {
    date: date.toLocaleDateString("fr-FR"),
    time: date.toLocaleTimeString("fr-FR", { hour: "2-digit", minute: "2-digit" }),
  };
}

function LoginForm({ onLogin }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    try {
      await login(username, password);
      onLogin();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="card">
      <h1>Connexion</h1>
      <form onSubmit={handleSubmit}>
        <label>
          Utilisateur
          <input value={username} onChange={(e) => setUsername(e.target.value)} required />
        </label>
        <label>
          Mot de passe
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </label>
        {error && <p className="error">{error}</p>}
        <button type="submit">Se connecter</button>
      </form>
    </div>
  );
}

function OrdersView({ user }) {
  const [orders, setOrders] = useState([]);
  const [allOrders, setAllOrders] = useState([]);
  const [view, setView] = useState("all");
  const [search, setSearch] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [refreshTick, setRefreshTick] = useState(0);
  const [newOrder, setNewOrder] = useState({
    invoice_number: "",
    store: "",
    client_name: "",
    product_name: "",
    sold_at: "",
  });

  useEffect(() => {
    const timer = setInterval(() => setRefreshTick((tick) => tick + 1), 15000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    async function load() {
      setLoading(true);
      setError("");
      try {
        const data = await listOrders({ view, q: search || undefined });
        setOrders(data);
        const fullData = await listOrders({ view: "all" });
        setAllOrders(fullData);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [view, search, refreshTick]);

  const counters = useMemo(() => {
    const total = allOrders.length;
    const toPrepare = allOrders.filter(
      (order) => !order.prepared && (!order.status || order.status !== "DEJA DONNER")
    ).length;
    const toBuild = allOrders.filter(
      (order) => order.prepared && !order.built && (!order.status || order.status !== "DEJA DONNER")
    ).length;
    const toDeliver = allOrders.filter((order) => order.built && !order.delivered).length;
    return { total, toPrepare, toBuild, toDeliver };
  }, [allOrders]);

  const canEditPrepared = user.role === "ADMIN" || user.role === "VENDOR";
  const canEditBuilt = user.role === "ADMIN" || user.role === "BUILDER";
  const canEditDelivered = user.role === "ADMIN" || user.role === "VENDOR";
  const canEditStatus = user.role === "ADMIN" || user.role === "VENDOR";

  async function handleToggle(order, field) {
    try {
      await updateOrder(order.id, { [field]: !order[field] });
      setRefreshTick((tick) => tick + 1);
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleStatusChange(order, value) {
    try {
      await updateOrder(order.id, { status: value || null });
      setRefreshTick((tick) => tick + 1);
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleCreateOrder(event) {
    event.preventDefault();
    setError("");
    try {
      await createOrder({
        ...newOrder,
        sold_at: new Date(newOrder.sold_at).toISOString(),
      });
      setNewOrder({ invoice_number: "", store: "", client_name: "", product_name: "", sold_at: "" });
      setRefreshTick((tick) => tick + 1);
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div>
      <div className="counters">
        <div className="counter">
          <span>Total</span>
          <strong>{counters.total}</strong>
        </div>
        <div className="counter">
          <span>Reste à préparer</span>
          <strong>{counters.toPrepare}</strong>
        </div>
        <div className="counter">
          <span>Reste à monter</span>
          <strong>{counters.toBuild}</strong>
        </div>
        <div className="counter">
          <span>Reste à livrer</span>
          <strong>{counters.toDeliver}</strong>
        </div>
      </div>

      <div className="toolbar">
        <div className="tabs">
          {views.map((item) => (
            <button
              key={item.key}
              className={item.key === view ? "active" : ""}
              onClick={() => setView(item.key)}
            >
              {item.label}
            </button>
          ))}
        </div>
        <input
          placeholder="Recherche..."
          value={search}
          onChange={(event) => setSearch(event.target.value)}
        />
      </div>

      {error && <p className="error">{error}</p>}
      {loading && <p>Chargement...</p>}

      <table>
        <thead>
          <tr>
            <th>Date</th>
            <th>Heure</th>
            <th>Produit</th>
            <th>Client</th>
            <th>Préparé</th>
            <th>Monté</th>
            <th>Livré</th>
            <th>Statut</th>
          </tr>
        </thead>
        <tbody>
          {orders.map((order) => {
            const { date, time } = formatDateTime(order.sold_at);
            return (
              <tr key={order.id}>
                <td>{date}</td>
                <td>{time}</td>
                <td>
                  <strong>{order.product_name}</strong>
                  <div className="muted">{order.invoice_number}</div>
                </td>
                <td>
                  <div>{order.client_name}</div>
                  <div className="muted">{order.store}</div>
                </td>
                <td>
                  <input
                    type="checkbox"
                    checked={order.prepared}
                    disabled={!canEditPrepared}
                    onChange={() => handleToggle(order, "prepared")}
                  />
                </td>
                <td>
                  <input
                    type="checkbox"
                    checked={order.built}
                    disabled={!canEditBuilt}
                    onChange={() => handleToggle(order, "built")}
                  />
                </td>
                <td>
                  <input
                    type="checkbox"
                    checked={order.delivered}
                    disabled={!canEditDelivered}
                    onChange={() => handleToggle(order, "delivered")}
                  />
                </td>
                <td>
                  <input
                    value={order.status || ""}
                    disabled={!canEditStatus}
                    onChange={(event) => handleStatusChange(order, event.target.value)}
                  />
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>

      {(user.role === "ADMIN" || user.role === "VENDOR") && (
        <form className="card" onSubmit={handleCreateOrder}>
          <h2>Nouvelle vente</h2>
          <div className="grid">
            <input
              placeholder="Facture"
              value={newOrder.invoice_number}
              onChange={(event) =>
                setNewOrder((prev) => ({ ...prev, invoice_number: event.target.value }))
              }
              required
            />
            <input
              placeholder="Magasin"
              value={newOrder.store}
              onChange={(event) => setNewOrder((prev) => ({ ...prev, store: event.target.value }))}
            />
            <input
              placeholder="Client"
              value={newOrder.client_name}
              onChange={(event) =>
                setNewOrder((prev) => ({ ...prev, client_name: event.target.value }))
              }
              required
            />
            <input
              placeholder="Produit"
              value={newOrder.product_name}
              onChange={(event) =>
                setNewOrder((prev) => ({ ...prev, product_name: event.target.value }))
              }
              required
            />
            <input
              type="datetime-local"
              value={newOrder.sold_at}
              onChange={(event) => setNewOrder((prev) => ({ ...prev, sold_at: event.target.value }))}
              required
            />
          </div>
          <button type="submit">Créer</button>
        </form>
      )}
    </div>
  );
}

function ImportView() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();
    if (!file) return;
    setError("");
    setResult(null);
    try {
      const data = await importInvoice(file);
      setResult(data);
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="card">
      <h2>Importer une facture PDF</h2>
      <form onSubmit={handleSubmit}>
        <input type="file" accept="application/pdf" onChange={(e) => setFile(e.target.files[0])} />
        <button type="submit" disabled={!file}>
          Importer
        </button>
      </form>
      {error && <p className="error">{error}</p>}
      {result && (
        <pre>{JSON.stringify(result, null, 2)}</pre>
      )}
    </div>
  );
}

function AdminView() {
  const [users, setUsers] = useState([]);
  const [error, setError] = useState("");
  const [newUser, setNewUser] = useState({ username: "", password: "", role: "VENDOR" });

  async function load() {
    setError("");
    try {
      const data = await listUsers();
      setUsers(data);
    } catch (err) {
      setError(err.message);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function handleCreate(event) {
    event.preventDefault();
    setError("");
    try {
      await createUser(newUser);
      setNewUser({ username: "", password: "", role: "VENDOR" });
      load();
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleRoleChange(userId, role) {
    setError("");
    try {
      await updateUser(userId, { role });
      load();
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleDelete(userId) {
    setError("");
    try {
      await deleteUser(userId);
      load();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="card">
      <h2>Gestion utilisateurs</h2>
      {error && <p className="error">{error}</p>}
      <table>
        <thead>
          <tr>
            <th>Utilisateur</th>
            <th>Rôle</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {users.map((user) => (
            <tr key={user.id}>
              <td>{user.username}</td>
              <td>
                <select value={user.role} onChange={(e) => handleRoleChange(user.id, e.target.value)}>
                  <option value="ADMIN">ADMIN</option>
                  <option value="VENDOR">VENDOR</option>
                  <option value="BUILDER">BUILDER</option>
                </select>
              </td>
              <td>
                <button onClick={() => handleDelete(user.id)}>Supprimer</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <form onSubmit={handleCreate}>
        <h3>Ajouter un utilisateur</h3>
        <div className="grid">
          <input
            placeholder="Utilisateur"
            value={newUser.username}
            onChange={(e) => setNewUser((prev) => ({ ...prev, username: e.target.value }))}
            required
          />
          <input
            placeholder="Mot de passe"
            type="password"
            value={newUser.password}
            onChange={(e) => setNewUser((prev) => ({ ...prev, password: e.target.value }))}
            required
          />
          <select
            value={newUser.role}
            onChange={(e) => setNewUser((prev) => ({ ...prev, role: e.target.value }))}
          >
            <option value="ADMIN">ADMIN</option>
            <option value="VENDOR">VENDOR</option>
            <option value="BUILDER">BUILDER</option>
          </select>
        </div>
        <button type="submit">Créer</button>
      </form>
    </div>
  );
}

export default function App() {
  const [user, setUser] = useState(null);
  const [page, setPage] = useState("orders");

  async function loadUser() {
    try {
      const data = await getMe();
      setUser(data);
    } catch (err) {
      setToken(null);
      setUser(null);
    }
  }

  useEffect(() => {
    loadUser();
  }, []);

  if (!user) {
    return <LoginForm onLogin={loadUser} />;
  }

  return (
    <div className="container">
      <header>
        <h1>Workflow PC Montage</h1>
        <div className="nav">
          <button className={page === "orders" ? "active" : ""} onClick={() => setPage("orders")}>
            Tableau
          </button>
          <button className={page === "import" ? "active" : ""} onClick={() => setPage("import")}>
            Importer facture
          </button>
          {user.role === "ADMIN" && (
            <button className={page === "admin" ? "active" : ""} onClick={() => setPage("admin")}>
              Admin
            </button>
          )}
        </div>
        <button
          className="ghost"
          onClick={() => {
            setToken(null);
            setUser(null);
          }}
        >
          Déconnexion
        </button>
      </header>

      {page === "orders" && <OrdersView user={user} />}
      {page === "import" && <ImportView />}
      {page === "admin" && <AdminView />}
    </div>
  );
}
