// src/App.jsx - TravelMate Enhanced
import { useState, useEffect, createContext, useContext } from 'react';
import './App.css';
import AdminDashboard from './AdminDashboard';

const API = 'http://localhost:8000';

// Auth Context
const AuthContext = createContext(null);
const useAuth = () => useContext(AuthContext);

function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));

  useEffect(() => {
    if (token) {
      fetch(`${API}/auth/me`, { headers: { Authorization: `Bearer ${token}` } })
        .then(r => r.ok ? r.json() : Promise.reject())
        .then(setUser)
        .catch(() => { setToken(null); localStorage.removeItem('token'); });
    }
  }, [token]);

  const login = async (email, password) => {
    const r = await fetch(`${API}/auth/login`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    if (!r.ok) throw new Error('Invalid credentials');
    const data = await r.json();
    localStorage.setItem('token', data.token);
    setToken(data.token);
    setUser(data.user);
  };

  const register = async (email, username, password) => {
    const r = await fetch(`${API}/auth/register`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, username, password })
    });
    if (!r.ok) throw new Error('Registration failed');
    const data = await r.json();
    localStorage.setItem('token', data.token);
    setToken(data.token);
    setUser(data.user);
  };

  const logout = () => {
    fetch(`${API}/auth/logout`, { method: 'POST', headers: { Authorization: `Bearer ${token}` } });
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
  };

  const authFetch = (url, opts = {}) => fetch(url, {
    ...opts, headers: { ...opts.headers, Authorization: `Bearer ${token}` }
  });

  return (
    <AuthContext.Provider value={{ user, token, login, register, logout, authFetch }}>
      {children}
    </AuthContext.Provider>
  );
}

// Auth Modal
function AuthModal({ onClose }) {
  const [isLogin, setIsLogin] = useState(true);
  const [form, setForm] = useState({ email: '', username: '', password: '' });
  const [error, setError] = useState('');
  const { login, register } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      if (isLogin) await login(form.email, form.password);
      else await register(form.email, form.username, form.password);
      onClose();
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal auth-modal" onClick={e => e.stopPropagation()}>
        <button className="close-btn" onClick={onClose}>×</button>
        <h2>{isLogin ? 'Welcome Back' : 'Create Account'}</h2>
        {error && <div className="error-msg">{error}</div>}
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Email</label>
            <input type="email" required value={form.email} onChange={e => setForm({...form, email: e.target.value})} />
          </div>
          {!isLogin && (
            <div className="form-group">
              <label>Username</label>
              <input required value={form.username} onChange={e => setForm({...form, username: e.target.value})} />
            </div>
          )}
          <div className="form-group">
            <label>Password</label>
            <input type="password" required value={form.password} onChange={e => setForm({...form, password: e.target.value})} />
          </div>
          <button type="submit" className="submit-btn">{isLogin ? 'Login' : 'Sign Up'}</button>
        </form>
        <p className="auth-switch">
          {isLogin ? "Don't have an account? " : "Already have an account? "}
          <button onClick={() => setIsLogin(!isLogin)}>{isLogin ? 'Sign Up' : 'Login'}</button>
        </p>
      </div>
    </div>
  );
}

// Navbar
function Navbar({ currentView, setCurrentView, onAuthClick, onAdminClick }) {
  const { user, logout } = useAuth();
  const isAdmin = user && (user.id === 1 || user.email.toLowerCase().includes('admin'));
  
  return (
    <nav className="navbar">
      <div className="nav-brand"><span className="logo">✈️</span><h1>TravelMate</h1></div>
      <div className="nav-links">
        {['explore', 'suggestions', 'trips', 'favorites'].map(v => (
          <button key={v} className={currentView === v ? 'active' : ''} onClick={() => setCurrentView(v)}>
            {v.charAt(0).toUpperCase() + v.slice(1)}
          </button>
        ))}
      </div>
      <div className="nav-user">
        {user ? (
          <>
            <span className="username">👤 {user.username}</span>
            {isAdmin && <button className="admin-btn" onClick={onAdminClick}>🛡️ Admin</button>}
            <button onClick={logout}>Logout</button>
          </>
        ) : (
          <button className="login-btn" onClick={onAuthClick}>Login</button>
        )}
      </div>
    </nav>
  );
}

// Weather Widget
function WeatherWidget({ destinationId }) {
  const [weather, setWeather] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API}/weather/${destinationId}`)
      .then(r => r.json())
      .then(setWeather)
      .finally(() => setLoading(false));
  }, [destinationId]);

  if (loading) return <div className="weather-widget loading">Loading weather...</div>;
  if (!weather) return null;

  const icons = { Sunny: '☀️', 'Partly Cloudy': '⛅', Cloudy: '☁️', Rainy: '🌧️', Clear: '☀️', Clouds: '☁️', Rain: '🌧️' };

  return (
    <div className="weather-widget">
      <h4>🌤️ Weather Forecast</h4>
      <div className="forecast-grid">
        {weather.forecast.slice(0, 5).map(day => (
          <div key={day.date} className="forecast-day">
            <span className="date">{new Date(day.date).toLocaleDateString('en', { weekday: 'short' })}</span>
            <span className="icon">{icons[day.condition] || '🌡️'}</span>
            <span className="temp">{day.temp_high}°/{day.temp_low}°</span>
          </div>
        ))}
      </div>
    </div>
  );
}

// Reviews Section
function ReviewsSection({ destinationId }) {
  const [reviews, setReviews] = useState([]);
  const [stats, setStats] = useState({ total: 0, distribution: {} });
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ rating: 5, title: '', content: '', travel_date: '' });
  const { user, authFetch } = useAuth();

  useEffect(() => {
    fetch(`${API}/reviews/${destinationId}`)
      .then(r => r.json())
      .then(data => { setReviews(data.reviews); setStats({ total: data.total, distribution: data.distribution }); });
  }, [destinationId]);

  const submitReview = async (e) => {
    e.preventDefault();
    await authFetch(`${API}/reviews`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ...form, destination_id: destinationId })
    });
    setShowForm(false);
    setForm({ rating: 5, title: '', content: '', travel_date: '' });
    const data = await fetch(`${API}/reviews/${destinationId}`).then(r => r.json());
    setReviews(data.reviews);
  };

  const markHelpful = async (reviewId) => {
    await authFetch(`${API}/reviews/${reviewId}/helpful`, { method: 'POST' });
    setReviews(reviews.map(r => r.id === reviewId ? { ...r, helpful_count: r.helpful_count + 1 } : r));
  };

  return (
    <div className="reviews-section">
      <div className="reviews-header">
        <h3>Reviews ({stats.total})</h3>
        {user && <button className="add-review-btn" onClick={() => setShowForm(!showForm)}>Write Review</button>}
      </div>
      
      <div className="rating-distribution">
        {[5, 4, 3, 2, 1].map(r => (
          <div key={r} className="rating-bar">
            <span>{r}★</span>
            <div className="bar"><div style={{ width: `${((stats.distribution[r] || 0) / stats.total) * 100}%` }} /></div>
            <span>{stats.distribution[r] || 0}</span>
          </div>
        ))}
      </div>

      {showForm && (
        <form className="review-form" onSubmit={submitReview}>
          <div className="star-rating">
            {[1, 2, 3, 4, 5].map(n => (
              <button type="button" key={n} className={form.rating >= n ? 'active' : ''} onClick={() => setForm({...form, rating: n})}>★</button>
            ))}
          </div>
          <input placeholder="Review title" required value={form.title} onChange={e => setForm({...form, title: e.target.value})} />
          <textarea placeholder="Share your experience..." required value={form.content} onChange={e => setForm({...form, content: e.target.value})} />
          <input type="date" value={form.travel_date} onChange={e => setForm({...form, travel_date: e.target.value})} />
          <button type="submit" className="submit-btn">Submit Review</button>
        </form>
      )}

      <div className="reviews-list">
        {reviews.map(r => (
          <div key={r.id} className="review-card">
            <div className="review-header">
              <span className="reviewer">👤 {r.username}</span>
              <span className="review-rating">{'★'.repeat(r.rating)}{'☆'.repeat(5 - r.rating)}</span>
            </div>
            <h4>{r.title}</h4>
            <p>{r.content}</p>
            <div className="review-footer">
              <span className="review-date">{r.travel_date && `Traveled: ${r.travel_date}`}</span>
              <button onClick={() => markHelpful(r.id)}>👍 Helpful ({r.helpful_count})</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// Flight Search
function FlightSearch({ destinationId, date }) {
  const [flights, setFlights] = useState([]);
  const [origin, setOrigin] = useState('JFK');
  const [loading, setLoading] = useState(false);

  const search = async () => {
    setLoading(true);
    const data = await fetch(`${API}/flights/search?origin=${origin}&destination_id=${destinationId}&date=${date}`).then(r => r.json());
    setFlights(data.flights || []);
    setLoading(false);
  };

  return (
    <div className="flight-search">
      <h4>✈️ Flights</h4>
      <div className="flight-form">
        <input placeholder="Origin (e.g., JFK)" value={origin} onChange={e => setOrigin(e.target.value)} />
        <button onClick={search} disabled={loading}>{loading ? 'Searching...' : 'Search Flights'}</button>
      </div>
      {flights.length > 0 && (
        <div className="flights-list">
          {flights.map((f, i) => (
            <div key={i} className="flight-card">
              <span className="airline">{f.airline}</span>
              <span className="times">{f.departure} → {f.arrival}</span>
              <span className="duration">{f.duration}</span>
              <span className="stops">{f.stops === 0 ? 'Direct' : `${f.stops} stop(s)`}</span>
              <span className="price">${f.price}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// Hotel Search
function HotelSearch({ destinationId, checkin, checkout }) {
  const [hotels, setHotels] = useState([]);
  const [loading, setLoading] = useState(false);

  const search = async () => {
    if (!checkin || !checkout) return alert('Please select dates');
    setLoading(true);
    const data = await fetch(`${API}/hotels/search?destination_id=${destinationId}&checkin=${checkin}&checkout=${checkout}`).then(r => r.json());
    setHotels(data.hotels || []);
    setLoading(false);
  };

  return (
    <div className="hotel-search">
      <h4>🏨 Hotels</h4>
      <button onClick={search} disabled={loading}>{loading ? 'Searching...' : 'Search Hotels'}</button>
      {hotels.length > 0 && (
        <div className="hotels-list">
          {hotels.map((h, i) => (
            <div key={i} className="hotel-card">
              <img src={h.image} alt={h.name} />
              <div className="hotel-info">
                <h5>{h.name} {'★'.repeat(h.stars)}</h5>
                <span className="hotel-rating">⭐ {h.rating} ({h.reviews} reviews)</span>
                <div className="amenities">{h.amenities.join(' • ')}</div>
                <span className="hotel-price">${h.price_per_night}/night</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// Share Modal
function ShareModal({ trip, onClose }) {
  const [shareUrl, setShareUrl] = useState('');
  const { authFetch } = useAuth();

  const createLink = async () => {
    const data = await authFetch(`${API}/trips/${trip.id}/share`, { method: 'POST' }).then(r => r.json());
    setShareUrl(`${window.location.origin}${data.share_url}`);
  };

  const share = (platform) => {
    const text = `Check out my trip to ${trip.destination_name}!`;
    const urls = {
      twitter: `https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}&url=${encodeURIComponent(shareUrl)}`,
      facebook: `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(shareUrl)}`,
      whatsapp: `https://wa.me/?text=${encodeURIComponent(text + ' ' + shareUrl)}`,
      email: `mailto:?subject=${encodeURIComponent('My Trip to ' + trip.destination_name)}&body=${encodeURIComponent(text + '\n\n' + shareUrl)}`
    };
    window.open(urls[platform], '_blank');
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal share-modal" onClick={e => e.stopPropagation()}>
        <button className="close-btn" onClick={onClose}>×</button>
        <h2>Share Your Trip</h2>
        <p>Share your trip to {trip.destination_name} with friends!</p>
        
        {!shareUrl ? (
          <button className="submit-btn" onClick={createLink}>Generate Share Link</button>
        ) : (
          <>
            <div className="share-link">
              <input readOnly value={shareUrl} />
              <button onClick={() => navigator.clipboard.writeText(shareUrl)}>Copy</button>
            </div>
            <div className="share-buttons">
              <button className="share-twitter" onClick={() => share('twitter')}>🐦 Twitter</button>
              <button className="share-facebook" onClick={() => share('facebook')}>📘 Facebook</button>
              <button className="share-whatsapp" onClick={() => share('whatsapp')}>💬 WhatsApp</button>
              <button className="share-email" onClick={() => share('email')}>📧 Email</button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

// Destination Detail Modal
function DestinationModal({ destination, onClose, onBook }) {
  const [tab, setTab] = useState('overview');
  const { user, authFetch } = useAuth();
  const [isFav, setIsFav] = useState(destination.is_favorite);

  const toggleFav = async () => {
    if (!user) return alert('Please login');
    await authFetch(`${API}/favorites/${destination.id}`, { method: isFav ? 'DELETE' : 'POST' });
    setIsFav(!isFav);
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal destination-modal" onClick={e => e.stopPropagation()}>
        <button className="close-btn" onClick={onClose}>×</button>
        <div className="dest-header" style={{ backgroundImage: `url(${destination.image_url})` }}>
          <div className="dest-header-overlay">
            <h2>{destination.name}, {destination.country}</h2>
            <p>{destination.description}</p>
            <button className={`fav-btn ${isFav ? 'active' : ''}`} onClick={toggleFav}>
              {isFav ? '❤️ Saved' : '🤍 Save'}
            </button>
          </div>
        </div>
        
        <div className="dest-tabs">
          {['overview', 'weather', 'flights', 'hotels', 'reviews'].map(t => (
            <button key={t} className={tab === t ? 'active' : ''} onClick={() => setTab(t)}>
              {t.charAt(0).toUpperCase() + t.slice(1)}
            </button>
          ))}
        </div>
        
        <div className="dest-content">
          {tab === 'overview' && (
            <div className="overview-tab">
              <div className="info-grid">
                <div className="info-item"><span>💰 Daily Budget</span><strong>${destination.avg_daily_cost}</strong></div>
                <div className="info-item"><span>✈️ Avg Flight</span><strong>${destination.flight_cost_estimate}</strong></div>
                <div className="info-item"><span>⭐ Rating</span><strong>{destination.rating}/5</strong></div>
                <div className="info-item"><span>📅 Best Months</span><strong>{destination.best_months?.split(',').map(m => ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][m-1]).join(', ')}</strong></div>
              </div>
              <button className="submit-btn" onClick={() => onBook(destination)}>Plan Trip</button>
            </div>
          )}
          {tab === 'weather' && <WeatherWidget destinationId={destination.id} />}
          {tab === 'flights' && <FlightSearch destinationId={destination.id} date={new Date().toISOString().split('T')[0]} />}
          {tab === 'hotels' && <HotelSearch destinationId={destination.id} checkin="" checkout="" />}
          {tab === 'reviews' && <ReviewsSection destinationId={destination.id} />}
        </div>
      </div>
    </div>
  );
}

// Booking Modal
function BookingModal({ destination, onClose }) {
  const [form, setForm] = useState({ start_date: '', end_date: '', num_travelers: 1, is_public: false });
  const [result, setResult] = useState(null);
  const { user, authFetch } = useAuth();

  const submit = async (e) => {
    e.preventDefault();
    if (!user) return alert('Please login to book');
    const data = await authFetch(`${API}/trips`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ...form, destination_id: destination.id })
    }).then(r => r.json());
    setResult(data);
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={e => e.stopPropagation()}>
        <button className="close-btn" onClick={onClose}>×</button>
        <h2>Plan Trip to {destination.name}</h2>
        
        {result ? (
          <div className="booking-result">
            <h3>🎉 Trip Booked!</h3>
            <div className="cost-summary">
              <p>✈️ Flights: <strong>${result.flight_price?.toLocaleString()}</strong></p>
              <p>🏨 Hotels: <strong>${result.hotel_price?.toLocaleString()}</strong></p>
              <p className="total">Total: <strong>${result.total_cost?.toLocaleString()}</strong></p>
            </div>
            <button className="submit-btn" onClick={onClose}>Done</button>
          </div>
        ) : (
          <form onSubmit={submit}>
            <div className="form-row">
              <div className="form-group">
                <label>Start Date</label>
                <input type="date" required value={form.start_date} onChange={e => setForm({...form, start_date: e.target.value})} />
              </div>
              <div className="form-group">
                <label>End Date</label>
                <input type="date" required value={form.end_date} onChange={e => setForm({...form, end_date: e.target.value})} />
              </div>
            </div>
            <div className="form-group">
              <label>Travelers</label>
              <input type="number" min="1" max="10" value={form.num_travelers} onChange={e => setForm({...form, num_travelers: +e.target.value})} />
            </div>
            <div className="form-group checkbox">
              <label><input type="checkbox" checked={form.is_public} onChange={e => setForm({...form, is_public: e.target.checked})} /> Make trip shareable</label>
            </div>
            <button type="submit" className="submit-btn">Book Trip</button>
          </form>
        )}
      </div>
    </div>
  );
}

// Destination Card
function DestinationCard({ dest, onClick, onFav }) {
  return (
    <div className="destination-card" onClick={() => onClick(dest)}>
      <div className="card-image" style={{ backgroundImage: `url(${dest.image_url})` }}>
        <span className="category-badge">{dest.category}</span>
        <span className="rating-badge">⭐ {dest.rating}</span>
        {dest.is_favorite !== undefined && (
          <button className="card-fav-btn" onClick={e => { e.stopPropagation(); onFav(dest); }}>
            {dest.is_favorite ? '❤️' : '🤍'}
          </button>
        )}
      </div>
      <div className="card-content">
        <h3>{dest.name}</h3>
        <p className="country">{dest.country}</p>
        <p className="description">{dest.description}</p>
        <div className="card-footer">
          <span className="daily-cost">${dest.avg_daily_cost}/day</span>
          <span className="flight-cost">✈️ ~${dest.flight_cost_estimate}</span>
        </div>
      </div>
    </div>
  );
}

// Trip Card with Share
function TripCard({ trip, onDelete, onShare }) {
  return (
    <div className="trip-card">
      <div className="card-image" style={{ backgroundImage: `url(${trip.image_url})` }}>
        <span className={`status-badge ${trip.status}`}>{trip.status}</span>
      </div>
      <div className="card-content">
        <h3>{trip.destination_name}, {trip.country}</h3>
        <div className="trip-details">
          <p>📅 {trip.start_date} → {trip.end_date}</p>
          <p>👥 {trip.num_travelers} traveler(s)</p>
          <p className="total-cost">💰 ${trip.total_cost?.toLocaleString()}</p>
        </div>
        <div className="trip-actions">
          <button className="share-btn" onClick={() => onShare(trip)}>🔗 Share</button>
          <button className="delete-btn" onClick={() => onDelete(trip.id)}>Cancel</button>
        </div>
      </div>
    </div>
  );
}

// Main App
function App() {
  const [view, setView] = useState('explore');
  const [destinations, setDestinations] = useState([]);
  const [categories, setCategories] = useState([]);
  const [selectedCat, setSelectedCat] = useState(null);
  const [suggestions, setSuggestions] = useState([]);
  const [trips, setTrips] = useState([]);
  const [favorites, setFavorites] = useState([]);
  const [selectedDest, setSelectedDest] = useState(null);
  const [bookingDest, setBookingDest] = useState(null);
  const [shareTrip, setShareTrip] = useState(null);
  const [showAuth, setShowAuth] = useState(false);
  const [showAdmin, setShowAdmin] = useState(false);
  const { user, token, authFetch } = useAuth();

  useEffect(() => {
    const url = selectedCat ? `${API}/destinations?category=${selectedCat}` : `${API}/destinations`;
    const headers = token ? { Authorization: `Bearer ${token}` } : {};
    fetch(url, { headers }).then(r => r.json()).then(setDestinations);
  }, [selectedCat, token]);

  useEffect(() => {
    fetch(`${API}/destinations/categories/list`).then(r => r.json()).then(setCategories);
  }, []);

  useEffect(() => {
    if (view === 'trips' && user) {
      authFetch(`${API}/trips`).then(r => r.json()).then(setTrips);
    }
  }, [view, user]);

  useEffect(() => {
    if (view === 'favorites' && user) {
      authFetch(`${API}/favorites`).then(r => r.json()).then(setFavorites);
    }
  }, [view, user]);

  const getSuggestions = async (params) => {
    const data = await fetch(`${API}/destinations/suggestions`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params)
    }).then(r => r.json());
    setSuggestions(data);
  };

  const toggleFav = async (dest) => {
    if (!user) return setShowAuth(true);
    await authFetch(`${API}/favorites/${dest.id}`, { method: dest.is_favorite ? 'DELETE' : 'POST' });
    setDestinations(destinations.map(d => d.id === dest.id ? { ...d, is_favorite: !d.is_favorite } : d));
  };

  const deleteTrip = async (id) => {
    if (!confirm('Cancel this trip?')) return;
    await authFetch(`${API}/trips/${id}`, { method: 'DELETE' });
    setTrips(trips.filter(t => t.id !== id));
  };

  return (
    <div className="app">
      <Navbar currentView={view} setCurrentView={setView} onAuthClick={() => setShowAuth(true)} onAdminClick={() => setShowAdmin(true)} />
      
      <main className="main-content">
        {view === 'explore' && (
          <>
            <h2>Explore Destinations</h2>
            <div className="category-filter">
              <button className={!selectedCat ? 'active' : ''} onClick={() => setSelectedCat(null)}>All</button>
              {categories.map(c => (
                <button key={c.id} className={selectedCat === c.id ? 'active' : ''} onClick={() => setSelectedCat(c.id)}>
                  {c.icon} {c.name}
                </button>
              ))}
            </div>
            <div className="destinations-grid">
              {destinations.map(d => <DestinationCard key={d.id} dest={d} onClick={setSelectedDest} onFav={toggleFav} />)}
            </div>
          </>
        )}

        {view === 'suggestions' && (
          <>
            <SuggestionForm onSubmit={getSuggestions} />
            {suggestions.length > 0 && (
              <div className="suggestions-grid">
                {suggestions.map(s => (
                  <div key={s.id} className="suggestion-card" onClick={() => setSelectedDest(s)}>
                    <div className="card-image" style={{ backgroundImage: `url(${s.image_url})` }}>
                      <div className="score-badge">Match: {Math.min(100, s.score)}%</div>
                    </div>
                    <div className="card-content">
                      <h3>{s.name}, {s.country}</h3>
                      <div className="reasons">{s.reasons.map((r, i) => <span key={i} className="reason-tag">✓ {r}</span>)}</div>
                      <div className="cost-breakdown">
                        <h4>Total: ${s.estimated_total_cost.toLocaleString()}</h4>
                        <small>Per person: ${s.cost_breakdown.per_person.toLocaleString()}</small>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </>
        )}

        {view === 'trips' && (
          <>
            <h2>My Trips</h2>
            {!user ? (
              <div className="empty-state"><p>Please login to view trips</p><button onClick={() => setShowAuth(true)}>Login</button></div>
            ) : trips.length === 0 ? (
              <div className="empty-state"><p>No trips yet</p><button onClick={() => setView('suggestions')}>Find Destinations</button></div>
            ) : (
              <div className="trips-grid">
                {trips.map(t => <TripCard key={t.id} trip={t} onDelete={deleteTrip} onShare={setShareTrip} />)}
              </div>
            )}
          </>
        )}

        {view === 'favorites' && (
          <>
            <h2>Saved Destinations</h2>
            {!user ? (
              <div className="empty-state"><p>Please login to view favorites</p><button onClick={() => setShowAuth(true)}>Login</button></div>
            ) : favorites.length === 0 ? (
              <div className="empty-state"><p>No saved destinations</p><button onClick={() => setView('explore')}>Explore</button></div>
            ) : (
              <div className="destinations-grid">
                {favorites.map(d => <DestinationCard key={d.id} dest={{...d, is_favorite: true}} onClick={setSelectedDest} onFav={toggleFav} />)}
              </div>
            )}
          </>
        )}
      </main>

      {showAuth && <AuthModal onClose={() => setShowAuth(false)} />}
      {selectedDest && <DestinationModal destination={selectedDest} onClose={() => setSelectedDest(null)} onBook={d => { setSelectedDest(null); setBookingDest(d); }} />}
      {bookingDest && <BookingModal destination={bookingDest} onClose={() => setBookingDest(null)} />}
      {shareTrip && <ShareModal trip={shareTrip} onClose={() => setShareTrip(null)} />}
      {showAdmin && token && <AdminDashboard token={token} onClose={() => setShowAdmin(false)} />}
    </div>
  );
}

// Suggestion Form Component
function SuggestionForm({ onSubmit }) {
  const [form, setForm] = useState({ budget_min: '', budget_max: '', month: new Date().getMonth() + 1, category: '', num_travelers: 1, duration_days: 7 });
  const months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];

  return (
    <div className="suggestion-form">
      <h2>Find Your Perfect Destination</h2>
      <div className="form-grid">
        <div className="form-group">
          <label>Budget Min (USD)</label>
          <input type="number" placeholder="e.g., 1000" value={form.budget_min} onChange={e => setForm({...form, budget_min: e.target.value})} />
        </div>
        <div className="form-group">
          <label>Budget Max (USD)</label>
          <input type="number" placeholder="e.g., 5000" value={form.budget_max} onChange={e => setForm({...form, budget_max: e.target.value})} />
        </div>
        <div className="form-group">
          <label>Travel Month</label>
          <select value={form.month} onChange={e => setForm({...form, month: +e.target.value})}>
            {months.map((m, i) => <option key={i} value={i + 1}>{m}</option>)}
          </select>
        </div>
        <div className="form-group">
          <label>Trip Type</label>
          <select value={form.category} onChange={e => setForm({...form, category: e.target.value})}>
            <option value="">Any</option>
            <option value="culture">Culture & History</option>
            <option value="beach">Beach & Relaxation</option>
            <option value="adventure">Adventure</option>
            <option value="city">City Break</option>
            <option value="luxury">Luxury</option>
          </select>
        </div>
        <div className="form-group">
          <label>Travelers</label>
          <input type="number" min="1" max="10" value={form.num_travelers} onChange={e => setForm({...form, num_travelers: +e.target.value})} />
        </div>
        <div className="form-group">
          <label>Duration (days)</label>
          <input type="number" min="1" max="30" value={form.duration_days} onChange={e => setForm({...form, duration_days: +e.target.value})} />
        </div>
      </div>
      <button className="submit-btn" onClick={() => onSubmit({ ...form, budget_min: form.budget_min ? +form.budget_min : null, budget_max: form.budget_max ? +form.budget_max : null, category: form.category || null })}>
        🔍 Find Destinations
      </button>
    </div>
  );
}

// Wrap App with Auth Provider
export default function AppWrapper() {
  return (
    <AuthProvider>
      <App />
    </AuthProvider>
  );
}