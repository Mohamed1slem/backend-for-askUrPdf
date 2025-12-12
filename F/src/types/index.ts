export interface Client {
  id: string;
  name: string;
  email: string;
  avatar?: string;
  lastMessage: string;
  lastMessageTime: Date;
  unread: boolean;
}

export interface Message {
  id: string;
  content: string;
  sender: 'employee' | 'client';
  timestamp: Date;
  attachments?: Document[];
}

export interface Document {
  id: string;
  title: string;
  category: DocumentCategory;
  content: string;
  similarity?: number;
  excerpt?: string;
  chunk: string; // Add this property

}

export type DocumentCategory = 'offers' | 'conventions' | 'guide-ngbss' | 'depot-vente';

export interface AIResponse {
  content: string;
  sources: Document[];
  isLoading?: boolean;
}
