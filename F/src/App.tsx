import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "@/contexts/AuthContext";
import Login from "./pages/Login";
import AdminDashboard from "./pages/admin/AdminDashboard";
import EmployeeManagement from "./pages/admin/EmployeeManagement";
import EmployeeDashboard from "./pages/employee/EmployeeDashboard";
import ClientMessages from "./pages/employee/ClientMessages";
import DocumentSearch from "./pages/employee/DocumentSearch";
import AIChatbot from "./pages/employee/AIChatbot";
import NotFound from "./pages/NotFound";
import Chat from "./pages/Chat"; // Ensure the file exists at ./pages/Chat.tsx

const queryClient = new QueryClient();

const ProtectedRoute: React.FC<{ children: React.ReactNode; requiredRole?: 'admin' | 'employee' }> = ({
  children,
  requiredRole,
}) => {
  const { isAuthenticated, user } = useAuth();

  if (!isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  if (requiredRole && user?.role !== requiredRole) {
    return <Navigate to={user?.role === 'admin' ? '/admin' : '/employee'} replace />;
  }

  return <>{children}</>;
};

const AppRoutes = () => {
  const { isAuthenticated, user } = useAuth();

  return (
    <Routes>
      <Route
        path="/"
        element={
          <Chat />
        }
      />
      
      {/* Admin Routes */}
      <Route
        path="/admin"
        element={
          <ProtectedRoute requiredRole="admin">
            <AdminDashboard />
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin/employees"
        element={
          <ProtectedRoute requiredRole="admin">
            <EmployeeManagement />
          </ProtectedRoute>
        }
      />

      {/* Employee Routes */}
      <Route
        path="/employee"
        element={
          <ProtectedRoute>
            <EmployeeDashboard />
          </ProtectedRoute>
        }
      />
      <Route
        path="/employee/messages"
        element={
          <ProtectedRoute>
            <ClientMessages />
          </ProtectedRoute>
        }
      />
      <Route
        path="/employee/documents"
        element={
          <ProtectedRoute>
            <DocumentSearch />
          </ProtectedRoute>
        }
      />
      <Route
        path="/employee/chatbot"
        element={
          <ProtectedRoute>
            <AIChatbot />
          </ProtectedRoute>
        }
      />

      <Route path="*" element={<NotFound />} />
    </Routes>
  );
};

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <AuthProvider>
          <AppRoutes />
        </AuthProvider>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
