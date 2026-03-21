import { useState, useEffect } from 'react'
import axios from 'axios'
import {
  LayoutDashboard, FolderKanban, CheckSquare, LogOut, Plus, Trash2,
  CheckCircle, Circle, Clock, TrendingUp, Users, Activity, Menu, X,
  ChevronRight, AlertCircle, Zap, Calendar
} from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts'

const API_URL = 'http://localhost:8000/api'

const COLORS = ['#00d4ff', '#10b981', '#f59e0b', '#ef4444']

function App() {
  const [token, setToken] = useState(localStorage.getItem('token'))
  const [user, setUser] = useState(null)
  const [activeTab, setActiveTab] = useState('dashboard')
  const [mobileMenu, setMobileMenu] = useState(false)
  
  useEffect(() => {
    if (token) {
      fetchUser()
    }
  }, [token])

  const api = axios.create({
    baseURL: API_URL,
    headers: token ? { Authorization: `Bearer ${token}` } : {}
  })

  const fetchUser = async () => {
    try {
      const res = await api.get('/salud')
      setUser({ nombre: 'Usuario', email: 'user@test.com' })
    } catch (e) {
      logout()
    }
  }

  const login = async (email, password) => {
    try {
      const res = await api.post('/login', { email, password })
      localStorage.setItem('token', res.data.token)
      setToken(res.data.token)
      setUser(res.data.usuario)
    } catch (e) {
      throw new Error(e.response?.data?.detail || 'Error en login')
    }
  }

  const registro = async (email, nombre, password) => {
    try {
      const res = await api.post('/registro', { email, nombre, password })
      localStorage.setItem('token', res.data.token)
      setToken(res.data.token)
      setUser(res.data.usuario)
    } catch (e) {
      throw new Error(e.response?.data?.detail || 'Error en registro')
    }
  }

  const logout = () => {
    localStorage.removeItem('token')
    setToken(null)
    setUser(null)
  }

  if (!token) {
    return <AuthPage onLogin={login} onRegister={registro} />
  }

  return (
    <div className="min-h-screen flex">
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} logout={logout} mobileMenu={mobileMenu} setMobileMenu={setMobileMenu} />
      <MainContent activeTab={activeTab} api={api} user={user} />
    </div>
  )
}

function AuthPage({ onLogin, onRegister }) {
  const [isLogin, setIsLogin] = useState(true)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [nombre, setNombre] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      if (isLogin) {
        await onLogin(email, password)
      } else {
        await onRegister(email, nombre, password)
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen w-full flex items-center justify-center p-4">
      <div className="card p-8 w-full max-w-md animate-fadeIn">
        <div className="text-center mb-8">
          <div className="w-16 h-16 rounded-full bg-gradient-to-r from-cyan-400 to-blue-500 mx-auto mb-4 flex items-center justify-center pulse-glow">
            <Zap className="w-8 h-8 text-black" />
          </div>
          <h1 className="text-2xl font-bold text-white mb-2">TaskFlow</h1>
          <p className="text-gray-400">Gestión de proyectos moderna</p>
        </div>

        <div className="flex mb-6 bg-white/5 rounded-xl p-1">
          <button
            onClick={() => setIsLogin(true)}
            className={`flex-1 py-2 rounded-lg transition-all ${isLogin ? 'bg-cyan-500 text-black font-semibold' : 'text-gray-400'}`}
          >
            Iniciar Sesión
          </button>
          <button
            onClick={() => setIsLogin(false)}
            className={`flex-1 py-2 rounded-lg transition-all ${!isLogin ? 'bg-cyan-500 text-black font-semibold' : 'text-gray-400'}`}
          >
            Registrarse
          </button>
        </div>

        {error && (
          <div className="bg-red-500/20 border border-red-500/50 rounded-xl p-3 mb-4 flex items-center gap-2">
            <AlertCircle className="w-5 h-5 text-red-400" />
            <span className="text-red-400 text-sm">{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {!isLogin && (
            <div>
              <label className="block text-gray-400 text-sm mb-2">Nombre</label>
              <input
                type="text"
                value={nombre}
                onChange={(e) => setNombre(e.target.value)}
                placeholder="Tu nombre"
                required
              />
            </div>
          )}
          <div>
            <label className="block text-gray-400 text-sm mb-2">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="correo@ejemplo.com"
              required
            />
          </div>
          <div>
            <label className="block text-gray-400 text-sm mb-2">Contraseña</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
            />
          </div>
          <button type="submit" className="btn-primary w-full" disabled={loading}>
            {loading ? 'Cargando...' : isLogin ? 'Entrar' : 'Crear Cuenta'}
          </button>
        </form>

        <p className="text-center text-gray-500 text-sm mt-6">
          {isLogin ? '¿No tienes cuenta?' : '¿Ya tienes cuenta?'}{' '}
          <button onClick={() => setIsLogin(!isLogin)} className="text-cyan-400 hover:text-cyan-300">
            {isLogin ? 'Regístrate' : 'Inicia sesión'}
          </button>
        </p>
      </div>
    </div>
  )
}

function Sidebar({ activeTab, setActiveTab, logout, mobileMenu, setMobileMenu }) {
  const menuItems = [
    { id: 'dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { id: 'proyectos', icon: FolderKanban, label: 'Proyectos' },
    { id: 'tareas', icon: CheckSquare, label: 'Tareas' },
  ]

  return (
    <>
      <aside className={`w-64 min-h-screen bg-black/20 border-r border-white/10 p-4 fixed lg:relative z-50 transition-transform ${mobileMenu ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}`}>
        <div className="flex items-center gap-3 mb-8">
          <div className="w-10 h-10 rounded-lg bg-gradient-to-r from-cyan-400 to-blue-500 flex items-center justify-center">
            <Zap className="w-5 h-5 text-black" />
          </div>
          <span className="font-bold text-lg">TaskFlow</span>
        </div>

        <nav className="space-y-2">
          {menuItems.map(({ id, icon: Icon, label }) => (
            <button
              key={id}
              onClick={() => { setActiveTab(id); setMobileMenu(false) }}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${
                activeTab === id
                  ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30'
                  : 'text-gray-400 hover:bg-white/5 hover:text-white'
              }`}
            >
              <Icon className="w-5 h-5" />
              <span>{label}</span>
              {activeTab === id && <ChevronRight className="w-4 h-4 ml-auto" />}
            </button>
          ))}
        </nav>

        <button
          onClick={logout}
          className="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-red-400 hover:bg-red-500/10 transition-all mt-8"
        >
          <LogOut className="w-5 h-5" />
          <span>Cerrar Sesión</span>
        </button>
      </aside>

      {mobileMenu && (
        <div className="fixed inset-0 bg-black/50 z-40 lg:hidden" onClick={() => setMobileMenu(false)} />
      )}
    </>
  )
}

function MainContent({ activeTab, api, user }) {
  const [mobileMenu, setMobileMenu] = useState(false)
  
  return (
    <main className="flex-1 min-h-screen p-4 lg:p-8 w-full">
      <header className="flex items-center justify-between mb-8">
        <div className="flex items-center gap-4">
          <button onClick={() => setMobileMenu(true)} className="lg:hidden p-2 hover:bg-white/10 rounded-lg">
            <Menu className="w-6 h-6" />
          </button>
          <div>
            <h1 className="text-2xl font-bold">
              {activeTab === 'dashboard' && 'Dashboard'}
              {activeTab === 'proyectos' && 'Proyectos'}
              {activeTab === 'tareas' && 'Tareas'}
            </h1>
            <p className="text-gray-400 text-sm">Bienvenido, {user?.nombre || 'Usuario'}</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-gradient-to-r from-cyan-400 to-blue-500 flex items-center justify-center text-black font-bold">
            {user?.nombre?.[0] || 'U'}
          </div>
        </div>
      </header>

      {activeTab === 'dashboard' && <Dashboard api={api} />}
      {activeTab === 'proyectos' && <Proyectos api={api} />}
      {activeTab === 'tareas' && <Tareas api={api} />}
    </main>
  )
}

function Dashboard({ api }) {
  const [stats, setStats] = useState({ proyectos: 0, tareas: 0, completadas: 0 })
  const [proyectos, setProyectos] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const res = await api.get('/proyectos')
      setProyectos(res.data)
      const tareasRes = await api.get('/tareas')
      setStats({
        proyectos: res.data.length,
        tareas: tareasRes.data.length,
        completadas: tareasRes.data.filter(t => t.estado === 'completada').length
      })
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  const statCards = [
    { label: 'Proyectos', value: stats.proyectos, icon: FolderKanban, color: 'from-cyan-400 to-blue-500' },
    { label: 'Tareas Totales', value: stats.tareas, icon: CheckSquare, color: 'from-purple-400 to-pink-500' },
    { label: 'Completadas', value: stats.completadas, icon: CheckCircle, color: 'from-green-400 to-emerald-500' },
    { label: 'Pendientes', value: stats.tareas - stats.completadas, icon: Clock, color: 'from-orange-400 to-yellow-500' },
  ]

  const chartData = [
    { name: 'Ene', tareas: 12, completadas: 8 },
    { name: 'Feb', tareas: 19, completadas: 15 },
    { name: 'Mar', tareas: 25, completadas: 20 },
    { name: 'Abr', tareas: 30, completadas: 28 },
    { name: 'May', tareas: 35, completadas: 32 },
  ]

  if (loading) {
    return <div className="flex items-center justify-center h-64"><Activity className="w-8 h-8 animate-spin text-cyan-400" /></div>
  }

  return (
    <div className="space-y-6 animate-fadeIn">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map(({ label, value, icon: Icon, color }) => (
          <div key={label} className="card p-6">
            <div className="flex items-center justify-between mb-4">
              <div className={`w-12 h-12 rounded-xl bg-gradient-to-r ${color} flex items-center justify-center`}>
                <Icon className="w-6 h-6 text-black" />
              </div>
              <span className="text-3xl font-bold">{value}</span>
            </div>
            <p className="text-gray-400 text-sm">{label}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-cyan-400" />
            Progreso Semanal
          </h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                <XAxis dataKey="name" stroke="#666" />
                <YAxis stroke="#666" />
                <Tooltip contentStyle={{ background: '#1a1a2e', border: '1px solid #333', borderRadius: '8px' }} />
                <Line type="monotone" dataKey="tareas" stroke="#00d4ff" strokeWidth={2} dot={{ fill: '#00d4ff' }} />
                <Line type="monotone" dataKey="completadas" stroke="#10b981" strokeWidth={2} dot={{ fill: '#10b981' }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="card p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <FolderKanban className="w-5 h-5 text-cyan-400" />
            Proyectos Recientes
          </h3>
          <div className="space-y-3">
            {proyectos.slice(0, 5).map((p) => (
              <div key={p.id} className="flex items-center justify-between p-3 bg-white/5 rounded-xl">
                <div>
                  <p className="font-medium">{p.nombre}</p>
                  <p className="text-sm text-gray-400">{p.descripcion || 'Sin descripción'}</p>
                </div>
                <ChevronRight className="w-5 h-5 text-gray-500" />
              </div>
            ))}
            {proyectos.length === 0 && (
              <p className="text-gray-500 text-center py-8">No hay proyectos aún</p>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

function Proyectos({ api }) {
  const [proyectos, setProyectos] = useState([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [nombre, setNombre] = useState('')
  const [descripcion, setDescripcion] = useState('')

  useEffect(() => {
    loadProyectos()
  }, [])

  const loadProyectos = async () => {
    try {
      const res = await api.get('/proyectos')
      setProyectos(res.data)
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  const crearProyecto = async (e) => {
    e.preventDefault()
    try {
      await api.post('/proyectos', { nombre, descripcion })
      setNombre('')
      setDescripcion('')
      setShowForm(false)
      loadProyectos()
    } catch (e) {
      console.error(e)
    }
  }

  return (
    <div className="space-y-6 animate-fadeIn">
      <div className="flex justify-between items-center">
        <p className="text-gray-400">Gestiona tus proyectos</p>
        <button onClick={() => setShowForm(!showForm)} className="btn-primary flex items-center gap-2">
          <Plus className="w-5 h-5" />
          Nuevo Proyecto
        </button>
      </div>

      {showForm && (
        <div className="card p-6 animate-fadeIn">
          <h3 className="text-lg font-semibold mb-4">Crear Proyecto</h3>
          <form onSubmit={crearProyecto} className="space-y-4">
            <div>
              <label className="block text-gray-400 text-sm mb-2">Nombre del proyecto</label>
              <input value={nombre} onChange={(e) => setNombre(e.target.value)} placeholder="Mi Proyecto" required />
            </div>
            <div>
              <label className="block text-gray-400 text-sm mb-2">Descripción</label>
              <textarea value={descripcion} onChange={(e) => setDescripcion(e.target.value)} placeholder="Descripción opcional" rows={3} />
            </div>
            <div className="flex gap-3">
              <button type="submit" className="btn-primary">Crear</button>
              <button type="button" onClick={() => setShowForm(false)} className="btn-secondary">Cancelar</button>
            </div>
          </form>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {proyectos.map((p) => (
          <div key={p.id} className="card p-6 hover:border-cyan-500/50">
            <div className="flex items-start justify-between mb-4">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-r from-cyan-400 to-blue-500 flex items-center justify-center">
                <FolderKanban className="w-6 h-6 text-black" />
              </div>
            </div>
            <h3 className="font-semibold text-lg mb-2">{p.nombre}</h3>
            <p className="text-gray-400 text-sm mb-4">{p.descripcion || 'Sin descripción'}</p>
            <div className="flex items-center gap-4 text-sm text-gray-500">
              <span className="flex items-center gap-1">
                <CheckSquare className="w-4 h-4" />
                {p.tareas_totales || 0} tareas
              </span>
              <span className="flex items-center gap-1">
                <CheckCircle className="w-4 h-4 text-green-400" />
                {p.tareas_completadas || 0}
              </span>
            </div>
          </div>
        ))}
      </div>

      {proyectos.length === 0 && !loading && (
        <div className="card p-12 text-center">
          <FolderKanban className="w-16 h-16 mx-auto mb-4 text-gray-600" />
          <h3 className="text-xl font-semibold mb-2">No hay proyectos</h3>
          <p className="text-gray-400 mb-4">Crea tu primer proyecto para comenzar</p>
          <button onClick={() => setShowForm(true)} className="btn-primary">
            Crear Proyecto
          </button>
        </div>
      )}
    </div>
  )
}

function Tareas({ api }) {
  const [tareas, setTareas] = useState([])
  const [proyectos, setProyectos] = useState([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [proyectoId, setProyectoId] = useState('')
  const [titulo, setTitulo] = useState('')
  const [prioridad, setPrioridad] = useState('media')
  const [filtroEstado, setFiltroEstado] = useState('')

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [tareasRes, proyectosRes] = await Promise.all([
        api.get('/tareas'),
        api.get('/proyectos')
      ])
      setTareas(tareasRes.data)
      setProyectos(proyectosRes.data)
      if (proyectosRes.data.length > 0) {
        setProyectoId(proyectosRes.data[0].id)
      }
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  const crearTarea = async (e) => {
    e.preventDefault()
    try {
      await api.post('/tareas', { titulo, prioridad, proyecto_id: proyectoId })
      setTitulo('')
      setShowForm(false)
      loadData()
    } catch (e) {
      console.error(e)
    }
  }

  const completarTarea = async (id) => {
    try {
      await api.patch(`/tareas/${id}`, { estado: 'completada' })
      loadData()
    } catch (e) {
      console.error(e)
    }
  }

  const eliminarTarea = async (id) => {
    try {
      await api.delete(`/tareas/${id}`)
      loadData()
    } catch (e) {
      console.error(e)
    }
  }

  const tareasFiltradas = filtroEstado
    ? tareas.filter(t => t.estado === filtroEstado)
    : tareas

  const prioridadColor = {
    baja: 'bg-gray-500/20 text-gray-400',
    media: 'bg-yellow-500/20 text-yellow-400',
    alta: 'bg-orange-500/20 text-orange-400',
    urgente: 'bg-red-500/20 text-red-400'
  }

  return (
    <div className="space-y-6 animate-fadeIn">
      <div className="flex flex-wrap justify-between items-center gap-4">
        <div className="flex gap-2">
          {['', 'pendiente', 'completada'].map((estado) => (
            <button
              key={estado}
              onClick={() => setFiltroEstado(estado)}
              className={`px-4 py-2 rounded-xl text-sm transition-all ${
                filtroEstado === estado
                  ? 'bg-cyan-500 text-black'
                  : 'bg-white/5 text-gray-400 hover:bg-white/10'
              }`}
            >
              {estado || 'Todas'}
            </button>
          ))}
        </div>
        <button onClick={() => setShowForm(!showForm)} className="btn-primary flex items-center gap-2">
          <Plus className="w-5 h-5" />
          Nueva Tarea
        </button>
      </div>

      {showForm && (
        <div className="card p-6 animate-fadeIn">
          <h3 className="text-lg font-semibold mb-4">Crear Tarea</h3>
          <form onSubmit={crearTarea} className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="md:col-span-2">
              <label className="block text-gray-400 text-sm mb-2">Título</label>
              <input value={titulo} onChange={(e) => setTitulo(e.target.value)} placeholder="Mi tarea" required />
            </div>
            <div>
              <label className="block text-gray-400 text-sm mb-2">Proyecto</label>
              <select value={proyectoId} onChange={(e) => setProyectoId(e.target.value)} required>
                {proyectos.map(p => (
                  <option key={p.id} value={p.id}>{p.nombre}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-gray-400 text-sm mb-2">Prioridad</label>
              <select value={prioridad} onChange={(e) => setPrioridad(e.target.value)}>
                <option value="baja">Baja</option>
                <option value="media">Media</option>
                <option value="alta">Alta</option>
                <option value="urgente">Urgente</option>
              </select>
            </div>
            <div className="md:col-span-4 flex gap-3">
              <button type="submit" className="btn-primary">Crear</button>
              <button type="button" onClick={() => setShowForm(false)} className="btn-secondary">Cancelar</button>
            </div>
          </form>
        </div>
      )}

      <div className="space-y-3">
        {tareasFiltradas.map((t) => (
          <div key={t.id} className="card p-4 flex items-center gap-4">
            <button
              onClick={() => completarTarea(t.id)}
              className={`w-6 h-6 rounded-full border-2 flex items-center justify-center transition-all ${
                t.estado === 'completada'
                  ? 'bg-green-500 border-green-500'
                  : 'border-gray-500 hover:border-cyan-400'
              }`}
            >
              {t.estado === 'completada' && <CheckCircle className="w-4 h-4 text-black" />}
            </button>
            <div className="flex-1">
              <p className={`font-medium ${t.estado === 'completada' ? 'line-through text-gray-500' : ''}`}>
                {t.titulo}
              </p>
              <span className={`text-xs px-2 py-1 rounded-full ${prioridadColor[t.prioridad]}`}>
                {t.prioridad}
              </span>
            </div>
            <button
              onClick={() => eliminarTarea(t.id)}
              className="p-2 hover:bg-red-500/20 rounded-lg text-red-400 transition-all"
            >
              <Trash2 className="w-5 h-5" />
            </button>
          </div>
        ))}
      </div>

      {tareasFiltradas.length === 0 && !loading && (
        <div className="card p-12 text-center">
          <CheckSquare className="w-16 h-16 mx-auto mb-4 text-gray-600" />
          <h3 className="text-xl font-semibold mb-2">No hay tareas</h3>
          <p className="text-gray-400 mb-4">Crea tu primera tarea</p>
        </div>
      )}
    </div>
  )
}

export default App
