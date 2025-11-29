// AdminDashboard.jsx - Complete Admin Panel
import { useState, useEffect } from 'react';
import './AdminDashboard.css';

const API = 'http://localhost:8000';

function AdminDashboard({ token, onClose }) {
  const [view, setView] = useState('dashboard');
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [destinations, setDestinations] = useState([]);
  const [trips, setTrips] = useState([]);
  const [reviews, setReviews] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const authFetch = (url, opts = {}) => fetch(url, {
    ...opts,
    headers: { ...opts.headers, Authorization: `Bearer ${token}` }
  });

  useEffect(() => {
    if (view === 'dashboard') loadDashboard();
    else if (view === 'users') loadUsers();
    else if (view === 'destinations') loadDestinations();
    else if (view === 'trips') loadTrips();
    else if (view === 'reviews') loadReviews();
    else if (view === 'analytics') loadAnalytics();
  }, [view]);

  const loadDashboard = async () => {
    setLoading(true);
    try {
      const data = await authFetch(`${API}/admin/dashboard/stats`).then(r => r.json());
      setStats(data);
    } catch (err) {
      setError('Failed to load dashboard. Are you an admin?');
    }
    setLoading(false);
  };

  const loadUsers = async () => {
    setLoading(true);
    try {
      const data = await authFetch(`${API}/admin/users`).then(r => r.json());
      setUsers(data.users);
    } catch (err) {
      setError('Failed to load users');
    }
    setLoading(false);
  };

  const loadDestinations = async () => {
    setLoading(true);
    try {
      const data = await authFetch(`${API}/destinations`).then(r => r.json());
      setDestinations(data);
    } catch (err) {
      setError('Failed to load destinations');
    }
    setLoading(false);
  };

  const loadTrips = async () => {
    setLoading(true);
    try {
      const data = await authFetch(`${API}/admin/trips/all`).then(r => r.json());
      setTrips(data);
    } catch (err) {
      setError('Failed to load trips');
    }
    setLoading(false);
  };

  const loadReviews = async () => {
    setLoading(true);
    try {
      const data = await authFetch(`${API}/admin/reviews/pending`).then(r => r.json());
      setReviews(data);
    } catch (err) {
      setError('Failed to load reviews');
    }
    setLoading(false);
  };

  const loadAnalytics = async () => {
    setLoading(true);
    try {
      const [revenue, userStats] = await Promise.all([
        authFetch(`${API}/admin/analytics/revenue`).then(r => r.json()),
        authFetch(`${API}/admin/analytics/users`).then(r => r.json())
      ]);
      setAnalytics({ revenue, users: userStats });
    } catch (err) {
      setError('Failed to load analytics');
    }
    setLoading(false);
  };

  const deleteUser = async (userId) => {
    if (!confirm('Delete this user and all their data?')) return;
    try {
      await authFetch(`${API}/admin/users/${userId}`, { method: 'DELETE' });
      loadUsers();
    } catch (err) {
      alert('Failed to delete user');
    }
  };

  const deleteDestination = async (destId) => {
    if (!confirm('Delete this destination?')) return;
    try {
      await authFetch(`${API}/admin/destinations/${destId}`, { method: 'DELETE' });
      loadDestinations();
    } catch (err) {
      alert('Failed to delete destination');
    }
  };

  const deleteReview = async (reviewId) => {
    if (!confirm('Delete this review?')) return;
    try {
      await authFetch(`${API}/admin/reviews/${reviewId}`, { method: 'DELETE' });
      loadReviews();
    } catch (err) {
      alert('Failed to delete review');
    }
  };

  return (
    <div className="admin-panel">
      <div className="admin-sidebar">
        <div className="admin-header">
          <h2>🛡️ Admin Panel</h2>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>
        <nav className="admin-nav">
          <button className={view === 'dashboard' ? 'active' : ''} onClick={() => setView('dashboard')}>
            📊 Dashboard
          </button>
          <button className={view === 'users' ? 'active' : ''} onClick={() => setView('users')}>
            👥 Users ({users.length})
          </button>
          <button className={view === 'destinations' ? 'active' : ''} onClick={() => setView('destinations')}>
            🌍 Destinations ({destinations.length})
          </button>
          <button className={view === 'trips' ? 'active' : ''} onClick={() => setView('trips')}>
            ✈️ Trips ({trips.length})
          </button>
          <button className={view === 'reviews' ? 'active' : ''} onClick={() => setView('reviews')}>
            ⭐ Reviews ({reviews.length})
          </button>
          <button className={view === 'analytics' ? 'active' : ''} onClick={() => setView('analytics')}>
            📈 Analytics
          </button>
        </nav>
      </div>

      <div className="admin-content">
        {error && <div className="admin-error">{error}</div>}
        {loading && <div className="admin-loading">Loading...</div>}

        {view === 'dashboard' && stats && (
          <div className="dashboard-view">
            <h1>Dashboard Overview</h1>
            
            <div className="stats-grid">
              <div className="stat-card">
                <span className="stat-icon">👥</span>
                <div>
                  <h3>{stats.totals.users}</h3>
                  <p>Total Users</p>
                  <small className="stat-change">+{stats.monthly.new_users} this month</small>
                </div>
              </div>
              <div className="stat-card">
                <span className="stat-icon">🌍</span>
                <div>
                  <h3>{stats.totals.destinations}</h3>
                  <p>Destinations</p>
                </div>
              </div>
              <div className="stat-card">
                <span className="stat-icon">✈️</span>
                <div>
                  <h3>{stats.totals.trips}</h3>
                  <p>Total Trips</p>
                  <small className="stat-change">+{stats.monthly.new_trips} this month</small>
                </div>
              </div>
              <div className="stat-card">
                <span className="stat-icon">⭐</span>
                <div>
                  <h3>{stats.totals.reviews}</h3>
                  <p>Reviews</p>
                  <small className="stat-change">+{stats.monthly.new_reviews} this month</small>
                </div>
              </div>
              <div className="stat-card highlight">
                <span className="stat-icon">💰</span>
                <div>
                  <h3>${stats.totals.revenue.toLocaleString()}</h3>
                  <p>Total Revenue</p>
                  <small className="stat-change">${stats.monthly.revenue.toLocaleString()} this month</small>
                </div>
              </div>
            </div>

            <div className="dashboard-sections">
              <div className="dashboard-section">
                <h3>🔥 Top Destinations</h3>
                <table className="admin-table">
                  <thead>
                    <tr>
                      <th>Destination</th>
                      <th>Country</th>
                      <th>Bookings</th>
                    </tr>
                  </thead>
                  <tbody>
                    {stats.top_destinations.map((d, i) => (
                      <tr key={i}>
                        <td>{d.name}</td>
                        <td>{d.country}</td>
                        <td><span className="badge">{d.bookings}</span></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <div className="dashboard-section">
                <h3>📋 Recent Activity</h3>
                <div className="activity-list">
                  {stats.recent_activities.map((a, i) => (
                    <div key={i} className="activity-item">
                      <span className="activity-icon">✈️</span>
                      <div>
                        <p><strong>{a.username}</strong> booked a trip to <strong>{a.destination}</strong></p>
                        <small>{new Date(a.created_at).toLocaleDateString()}</small>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {view === 'users' && (
          <div className="users-view">
            <h1>User Management</h1>
            <table className="admin-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Username</th>
                  <th>Email</th>
                  <th>Trips</th>
                  <th>Reviews</th>
                  <th>Joined</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {users.map(u => (
                  <tr key={u.id}>
                    <td>{u.id}</td>
                    <td>{u.username}</td>
                    <td>{u.email}</td>
                    <td><span className="badge">{u.trip_count}</span></td>
                    <td><span className="badge">{u.review_count}</span></td>
                    <td>{new Date(u.created_at).toLocaleDateString()}</td>
                    <td>
                      <button className="btn-delete" onClick={() => deleteUser(u.id)}>Delete</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {view === 'destinations' && (
          <div className="destinations-view">
            <h1>Destination Management</h1>
            <table className="admin-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Name</th>
                  <th>Country</th>
                  <th>Category</th>
                  <th>Daily Cost</th>
                  <th>Rating</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {destinations.map(d => (
                  <tr key={d.id}>
                    <td>{d.id}</td>
                    <td>{d.name}</td>
                    <td>{d.country}</td>
                    <td><span className="badge">{d.category}</span></td>
                    <td>${d.avg_daily_cost}</td>
                    <td>⭐ {d.rating}</td>
                    <td>
                      <button className="btn-delete" onClick={() => deleteDestination(d.id)}>Delete</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {view === 'trips' && (
          <div className="trips-view">
            <h1>Trip Management</h1>
            <table className="admin-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>User</th>
                  <th>Destination</th>
                  <th>Dates</th>
                  <th>Cost</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {trips.map(t => (
                  <tr key={t.id}>
                    <td>{t.id}</td>
                    <td>{t.username}</td>
                    <td>{t.destination_name}, {t.country}</td>
                    <td>{t.start_date} → {t.end_date}</td>
                    <td>${t.total_cost?.toLocaleString()}</td>
                    <td><span className={`status-badge ${t.status}`}>{t.status}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {view === 'reviews' && (
          <div className="reviews-view">
            <h1>Review Moderation</h1>
            <div className="reviews-list-admin">
              {reviews.map(r => (
                <div key={r.id} className="review-card-admin">
                  <div className="review-header">
                    <div>
                      <strong>{r.username}</strong> · {r.destination_name}
                      <span className="review-rating">{'⭐'.repeat(r.rating)}</span>
                    </div>
                    <button className="btn-delete" onClick={() => deleteReview(r.id)}>Delete</button>
                  </div>
                  <h4>{r.title}</h4>
                  <p>{r.content}</p>
                  <small>{new Date(r.created_at).toLocaleDateString()}</small>
                </div>
              ))}
            </div>
          </div>
        )}

        {view === 'analytics' && analytics && (
          <div className="analytics-view">
            <h1>Analytics & Reports</h1>
            
            <div className="chart-section">
              <h3>📊 Monthly Revenue</h3>
              <div className="chart-bars">
                {analytics.revenue.monthly.map((m, i) => (
                  <div key={i} className="chart-bar">
                    <div className="bar" style={{ height: `${(m.revenue / 10000) * 100}%` }}></div>
                    <span className="bar-label">{m.month}</span>
                    <span className="bar-value">${m.revenue?.toLocaleString()}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="chart-section">
              <h3>🌍 Revenue by Destination</h3>
              <table className="admin-table">
                <thead>
                  <tr>
                    <th>Destination</th>
                    <th>Bookings</th>
                    <th>Revenue</th>
                  </tr>
                </thead>
                <tbody>
                  {analytics.revenue.by_destination.map((d, i) => (
                    <tr key={i}>
                      <td>{d.name}, {d.country}</td>
                      <td><span className="badge">{d.bookings}</span></td>
                      <td>${d.revenue?.toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default AdminDashboard;