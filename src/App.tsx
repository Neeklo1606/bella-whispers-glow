import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Index from "./pages/Index";
import Pricing from "./pages/Pricing";
import Login from "./pages/Login";
import Consent from "./pages/Consent";
import Dashboard from "./pages/Dashboard";
import Feed from "./pages/Feed";
import Favorites from "./pages/Favorites";
import Profile from "./pages/Profile";
import SubscriptionManagement from "./pages/SubscriptionManagement";
import AdminDashboard from "./pages/AdminDashboard";
import AdminUsers from "./pages/AdminUsers";
import { DashboardLayout } from "./components/layout/DashboardLayout";
import { AdminLayout } from "./components/layout/AdminLayout";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Routes>
          {/* Marketing */}
          <Route path="/" element={<Index />} />
          <Route path="/pricing" element={<Pricing />} />

          {/* Auth */}
          <Route path="/login" element={<Login />} />
          <Route path="/consent" element={<Consent />} />

          {/* Dashboard */}
          <Route path="/dashboard" element={<DashboardLayout />}>
            <Route index element={<Dashboard />} />
            <Route path="feed" element={<Feed />} />
            <Route path="favorites" element={<Favorites />} />
            <Route path="profile" element={<Profile />} />
            <Route path="subscription" element={<SubscriptionManagement />} />
          </Route>

          {/* Admin */}
          <Route path="/admin" element={<AdminLayout />}>
            <Route index element={<AdminDashboard />} />
            <Route path="users" element={<AdminUsers />} />
          </Route>

          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
