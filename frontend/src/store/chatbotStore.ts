import { create } from 'zustand';

export interface ChatContextData {
  vessel_position?: { lat: number; lon: number };
  vessel_speed?: number;
  selected_route?: any;
  candidate_routes?: any[];
  iceberg_id?: string;
  hazard?: any;
  navigation_status?: string;
}

interface ChatbotState {
  isOpen: boolean;
  toggleOpen: () => void;
  setOpen: (val: boolean) => void;
  contextData: ChatContextData;
  updateContext: (data: Partial<ChatContextData>) => void;
}

export const useChatbotStore = create<ChatbotState>((set) => ({
  isOpen: false,
  toggleOpen: () => set((state) => ({ isOpen: !state.isOpen })),
  setOpen: (val) => set({ isOpen: val }),
  contextData: {},
  updateContext: (data) => set((state) => ({ 
    contextData: { ...state.contextData, ...data } 
  }))
}));
