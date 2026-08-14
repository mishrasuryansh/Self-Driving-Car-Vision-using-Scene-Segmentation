/**
 * Main Application Component & React Router Configuration (T059, T060, T062, T063).
 *
 * Configures client-side routing, global AuthProvider context wrapper,
 * and ProtectedRoute authentication guards.
 */

import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import { Layout } from './components/Layout';
import { DashboardPage } from './pages/DashboardPage';
import { UploadImagePage } from './pages/UploadImagePage';
import { UploadVideoPage } from './pages/UploadVideoPage';
import { HistoryPage } from './pages/HistoryPage';
import { AnalyticsPage } from './pages/AnalyticsPage';
import { SettingsPage } from './pages/SettingsPage';
import { AboutPage } from './pages/AboutPage';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';

export const App: React.FC = () => {
  return (
    <Router>
      <AuthProvider>
        <Layout>
          <Routes>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/about" element={<AboutPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />

            {/* Protected Routes (T063) */}
            <Route
              path="/upload/image"
              element={
                <ProtectedRoute>
                  <UploadImagePage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/upload/video"
              element={
                <ProtectedRoute>
                  <UploadVideoPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/history"
              element={
                <ProtectedRoute>
                  <HistoryPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/analytics"
              element={
                <ProtectedRoute>
                  <AnalyticsPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/settings"
              element={
                <ProtectedRoute>
                  <SettingsPage />
                </ProtectedRoute>
              }
            />
          </Routes>
        </Layout>
      </AuthProvider>
    </Router>
  );
};

export default App;
