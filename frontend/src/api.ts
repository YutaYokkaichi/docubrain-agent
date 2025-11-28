import axios from 'axios';
import type { ChatResponse } from './types';

// .env で設定した Cloud Run の URL を読み込む
const API_URL = import.meta.env.VITE_API_URL;

// チャットAPIを叩く関数
export const sendMessage = async (message: string): Promise<ChatResponse> => {
    try {
        const response = await axios.post<ChatResponse>(`${API_URL}/api/chat`, {
            message: message,
        });
        return response.data;
    } catch (error) {
        console.error("API Error:", error);
        throw error;
    }
};