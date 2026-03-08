import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  getTelegramInitData,
  authenticateTelegram,
  setUserToken,
  getUserToken,
  isUserAuthenticated,
  removeUserToken,
} from "@/lib/api";
import { useToast } from "@/hooks/use-toast";

/**
 * Hook for Telegram WebApp authentication.
 */
export function useTelegramAuth() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [isInitialized, setIsInitialized] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const initTelegram = async () => {
      // Check if Telegram WebApp is available
      if (typeof window === "undefined" || !window.Telegram?.WebApp) {
        console.warn("Telegram WebApp not available");
        setIsLoading(false);
        setIsInitialized(false);
        return;
      }

      // Initialize Telegram WebApp
      window.Telegram.WebApp.ready();
      window.Telegram.WebApp.expand();

      setIsInitialized(true);

      // Check if user is already authenticated
      if (isUserAuthenticated()) {
        setIsAuthenticated(true);
        setIsLoading(false);
        return;
      }

      // Try to authenticate with Telegram initData
      const initData = getTelegramInitData();
      if (initData) {
        try {
          setIsLoading(true);
          const response = await authenticateTelegram(initData);
          setUserToken(response.access_token);
          setIsAuthenticated(true);
          toast({
            title: "Успешная авторизация",
            description: `Добро пожаловать, ${response.user.first_name}!`,
          });
        } catch (error) {
          console.error("Telegram authentication failed:", error);
          toast({
            title: "Ошибка авторизации",
            description: error instanceof Error ? error.message : "Не удалось авторизоваться",
            variant: "destructive",
          });
          setIsAuthenticated(false);
        } finally {
          setIsLoading(false);
        }
      } else {
        setIsLoading(false);
      }
    };

    initTelegram();
  }, [toast]);

  const login = async () => {
    const initData = getTelegramInitData();
    if (!initData) {
      toast({
        title: "Ошибка",
        description: "Telegram WebApp не доступен",
        variant: "destructive",
      });
      return;
    }

    try {
      setIsLoading(true);
      const response = await authenticateTelegram(initData);
      setUserToken(response.access_token);
      setIsAuthenticated(true);
      toast({
        title: "Успешная авторизация",
        description: `Добро пожаловать, ${response.user.first_name}!`,
      });
      navigate("/dashboard/profile");
    } catch (error) {
      toast({
        title: "Ошибка авторизации",
        description: error instanceof Error ? error.message : "Не удалось авторизоваться",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    removeUserToken();
    setIsAuthenticated(false);
    navigate("/");
  };

  return {
    isInitialized,
    isAuthenticated,
    isLoading,
    login,
    logout,
    telegramUser: window.Telegram?.WebApp?.initDataUnsafe?.user,
  };
}
