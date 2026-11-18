import React from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import Navbar from './components/Navbar'
import Footer from './components/Footer'
import ProtectedRoute from './components/ProtectedRoute'

import LandingPage from './pages/LandingPage'
import Login from './pages/Login'
import RoleSelection from './pages/RoleSelection'
import DonorRegister from './pages/DonorRegister'
import ReceiverRegister from './pages/ReceiverRegister'
import DonorDashboard from './pages/DonorDashboard'
import CreateDonation from './pages/CreateDonation'
import DonationDetails from './pages/DonationDetails'
import ReceiverDashboard from './pages/ReceiverDashboard'
import DemandManagement from './pages/DemandManagement'
import VolunteerDashboard from './pages/VolunteerDashboard'
import AdminDashboard from './pages/AdminDashboard'
import ResearchDashboard from './pages/ResearchDashboard'

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <div className="min-h-screen flex flex-col bg-gray-50">
          <Navbar />
          <main className="flex-1">
            <Routes>
              {/* Public routes */}
              <Route path="/" element={<LandingPage />} />
              <Route path="/login" element={<Login />} />
              <Route path="/role-selection" element={<RoleSelection />} />
              <Route path="/register/donor" element={<DonorRegister />} />
              <Route path="/register/receiver" element={<ReceiverRegister />} />

              {/* Research dashboard - accessible to all (academic showcase) */}
              <Route path="/research" element={<ResearchDashboard />} />

              {/* Donor routes */}
              <Route
                path="/donor"
                element={
                  <ProtectedRoute allowedRoles={['ROLE_DONOR']}>
                    <DonorDashboard />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/donor/create"
                element={
                  <ProtectedRoute allowedRoles={['ROLE_DONOR']}>
                    <CreateDonation />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/donations/:id"
                element={
                  <ProtectedRoute allowedRoles={['ROLE_DONOR', 'ROLE_ADMIN']}>
                    <DonationDetails />
                  </ProtectedRoute>
                }
              />

              {/* Receiver routes */}
              <Route
                path="/receiver"
                element={
                  <ProtectedRoute allowedRoles={['ROLE_RECEIVER']}>
                    <ReceiverDashboard />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/receiver/demands"
                element={
                  <ProtectedRoute allowedRoles={['ROLE_RECEIVER']}>
                    <DemandManagement />
                  </ProtectedRoute>
                }
              />

              {/* Volunteer routes */}
              <Route
                path="/volunteer"
                element={
                  <ProtectedRoute allowedRoles={['ROLE_VOLUNTEER', 'ROLE_ADMIN']}>
                    <VolunteerDashboard />
                  </ProtectedRoute>
                }
              />

              {/* Admin routes */}
              <Route
                path="/admin"
                element={
                  <ProtectedRoute allowedRoles={['ROLE_ADMIN']}>
                    <AdminDashboard />
                  </ProtectedRoute>
                }
              />

              {/* Catch-all */}
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>
          <Footer />
        </div>
      </BrowserRouter>
    </AuthProvider>
  )
}

export default App
