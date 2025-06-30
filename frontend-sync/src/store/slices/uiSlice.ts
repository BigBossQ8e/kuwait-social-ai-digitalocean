// UI state slice for global UI management

import { createSlice, type PayloadAction } from '@reduxjs/toolkit';

export interface NotificationState {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  message: string;
  title?: string;
  duration?: number;
  action?: {
    label: string;
    handler: () => void;
  };
}

export interface ModalState {
  id: string;
  type: string;
  props?: Record<string, any>;
  onClose?: () => void;
}

export interface UIState {
  theme: 'light' | 'dark' | 'auto';
  language: 'en' | 'ar';
  direction: 'ltr' | 'rtl';
  sidebarOpen: boolean;
  sidebarCollapsed: boolean;
  loading: {
    global: boolean;
    components: Record<string, boolean>;
  };
  notifications: NotificationState[];
  modals: ModalState[];
  breadcrumb: {
    items: Array<{
      label: string;
      href?: string;
    }>;
  };
  pageTitle: string;
  errors: {
    global: string | null;
    field: Record<string, string>;
  };
}

const initialState: UIState = {
  theme: (localStorage.getItem('theme') as 'light' | 'dark' | 'auto') || 'light',
  language: (localStorage.getItem('language') as 'en' | 'ar') || 'en',
  direction: (localStorage.getItem('language') === 'ar') ? 'rtl' : 'ltr',
  sidebarOpen: true,
  sidebarCollapsed: false,
  loading: {
    global: false,
    components: {},
  },
  notifications: [],
  modals: [],
  breadcrumb: {
    items: [],
  },
  pageTitle: 'Kuwait Social AI',
  errors: {
    global: null,
    field: {},
  },
};

const uiSlice = createSlice({
  name: 'ui',
  initialState,
  reducers: {
    setTheme: (state, action: PayloadAction<'light' | 'dark' | 'auto'>) => {
      state.theme = action.payload;
      localStorage.setItem('theme', action.payload);
    },
    
    setLanguage: (state, action: PayloadAction<'en' | 'ar'>) => {
      state.language = action.payload;
      state.direction = action.payload === 'ar' ? 'rtl' : 'ltr';
      localStorage.setItem('language', action.payload);
    },
    
    toggleSidebar: (state) => {
      state.sidebarOpen = !state.sidebarOpen;
    },
    
    setSidebarOpen: (state, action: PayloadAction<boolean>) => {
      state.sidebarOpen = action.payload;
    },
    
    toggleSidebarCollapsed: (state) => {
      state.sidebarCollapsed = !state.sidebarCollapsed;
    },
    
    setSidebarCollapsed: (state, action: PayloadAction<boolean>) => {
      state.sidebarCollapsed = action.payload;
    },
    
    setGlobalLoading: (state, action: PayloadAction<boolean>) => {
      state.loading.global = action.payload;
    },
    
    setComponentLoading: (
      state,
      action: PayloadAction<{ component: string; loading: boolean }>
    ) => {
      const { component, loading } = action.payload;
      if (loading) {
        state.loading.components[component] = true;
      } else {
        delete state.loading.components[component];
      }
    },
    
    addNotification: (state, action: PayloadAction<Omit<NotificationState, 'id'>>) => {
      const id = Date.now().toString();
      state.notifications.push({
        id,
        duration: 5000, // 5 seconds default
        ...action.payload,
      });
    },
    
    removeNotification: (state, action: PayloadAction<string>) => {
      state.notifications = state.notifications.filter(
        (notification) => notification.id !== action.payload
      );
    },
    
    clearNotifications: (state) => {
      state.notifications = [];
    },
    
    openModal: (state, action: PayloadAction<Omit<ModalState, 'id'>>) => {
      const id = Date.now().toString();
      state.modals.push({
        id,
        ...action.payload,
      });
    },
    
    closeModal: (state, action: PayloadAction<string>) => {
      const modalIndex = state.modals.findIndex((modal) => modal.id === action.payload);
      if (modalIndex !== -1) {
        const modal = state.modals[modalIndex];
        if (modal.onClose) {
          modal.onClose();
        }
        state.modals.splice(modalIndex, 1);
      }
    },
    
    closeTopModal: (state) => {
      if (state.modals.length > 0) {
        const topModal = state.modals[state.modals.length - 1];
        if (topModal.onClose) {
          topModal.onClose();
        }
        state.modals.pop();
      }
    },
    
    clearModals: (state) => {
      state.modals.forEach((modal) => {
        if (modal.onClose) {
          modal.onClose();
        }
      });
      state.modals = [];
    },
    
    setBreadcrumb: (
      state,
      action: PayloadAction<Array<{ label: string; href?: string }>>
    ) => {
      state.breadcrumb.items = action.payload;
    },
    
    setPageTitle: (state, action: PayloadAction<string>) => {
      state.pageTitle = action.payload;
      document.title = `${action.payload} - Kuwait Social AI`;
    },
    
    setGlobalError: (state, action: PayloadAction<string | null>) => {
      state.errors.global = action.payload;
    },
    
    setFieldError: (
      state,
      action: PayloadAction<{ field: string; error: string | null }>
    ) => {
      const { field, error } = action.payload;
      if (error) {
        state.errors.field[field] = error;
      } else {
        delete state.errors.field[field];
      }
    },
    
    clearErrors: (state) => {
      state.errors.global = null;
      state.errors.field = {};
    },
  },
});

export const {
  setTheme,
  setLanguage,
  toggleSidebar,
  setSidebarOpen,
  toggleSidebarCollapsed,
  setSidebarCollapsed,
  setGlobalLoading,
  setComponentLoading,
  addNotification,
  removeNotification,
  clearNotifications,
  openModal,
  closeModal,
  closeTopModal,
  clearModals,
  setBreadcrumb,
  setPageTitle,
  setGlobalError,
  setFieldError,
  clearErrors,
} = uiSlice.actions;

export default uiSlice.reducer;

// Selectors
export const selectTheme = (state: { ui: UIState }) => state.ui.theme;
export const selectLanguage = (state: { ui: UIState }) => state.ui.language;
export const selectDirection = (state: { ui: UIState }) => state.ui.direction;
export const selectSidebarOpen = (state: { ui: UIState }) => state.ui.sidebarOpen;
export const selectSidebarCollapsed = (state: { ui: UIState }) => state.ui.sidebarCollapsed;
export const selectGlobalLoading = (state: { ui: UIState }) => state.ui.loading.global;
export const selectComponentLoading = (component: string) => (state: { ui: UIState }) =>
  state.ui.loading.components[component] || false;
export const selectNotifications = (state: { ui: UIState }) => state.ui.notifications;
export const selectModals = (state: { ui: UIState }) => state.ui.modals;
export const selectBreadcrumb = (state: { ui: UIState }) => state.ui.breadcrumb.items;
export const selectPageTitle = (state: { ui: UIState }) => state.ui.pageTitle;
export const selectGlobalError = (state: { ui: UIState }) => state.ui.errors.global;
export const selectFieldErrors = (state: { ui: UIState }) => state.ui.errors.field;