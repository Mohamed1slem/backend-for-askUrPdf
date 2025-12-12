import { Client, Message, Document } from '@/types';

export const mockClients: Client[] = [
  {
    id: '1',
    name: 'Marie Dubois',
    email: 'marie.dubois@example.com',
    lastMessage: "Bonjour, je voudrais des informations sur vos offres commerciales...",
    lastMessageTime: new Date(Date.now() - 1000 * 60 * 5),
    unread: true,
  },
  {
    id: '2',
    name: 'Pierre Martin',
    email: 'pierre.martin@example.com',
    lastMessage: "Concernant le dépôt vente, quelles sont les conditions?",
    lastMessageTime: new Date(Date.now() - 1000 * 60 * 30),
    unread: true,
  },
  {
    id: '3',
    name: 'Sophie Bernard',
    email: 'sophie.bernard@example.com',
    lastMessage: "Merci pour votre réponse rapide!",
    lastMessageTime: new Date(Date.now() - 1000 * 60 * 60 * 2),
    unread: false,
  },
  {
    id: '4',
    name: 'Jean Lefebvre',
    email: 'jean.lefebvre@example.com',
    lastMessage: "J'ai besoin du guide NGBSS pour le nouveau système...",
    lastMessageTime: new Date(Date.now() - 1000 * 60 * 60 * 5),
    unread: false,
  },
  {
    id: '5',
    name: 'Claire Moreau',
    email: 'claire.moreau@example.com',
    lastMessage: "Pouvez-vous m'envoyer la convention signée?",
    lastMessageTime: new Date(Date.now() - 1000 * 60 * 60 * 24),
    unread: false,
  },
];

export const mockConversations: Record<string, Message[]> = {
  '1': [
    {
      id: 'm1',
      content: "Bonjour, je voudrais des informations sur vos offres commerciales. Quels sont les tarifs pour une entreprise de 50 employés?",
      sender: 'client',
      timestamp: new Date(Date.now() - 1000 * 60 * 5),
    },
  ],
  '2': [
    {
      id: 'm1',
      content: "Bonjour, je suis intéressé par vos services.",
      sender: 'client',
      timestamp: new Date(Date.now() - 1000 * 60 * 60),
    },
    {
      id: 'm2',
      content: "Bonjour M. Martin, merci pour votre intérêt. Comment puis-je vous aider?",
      sender: 'employee',
      timestamp: new Date(Date.now() - 1000 * 60 * 45),
    },
    {
      id: 'm3',
      content: "Concernant le dépôt vente, quelles sont les conditions?",
      sender: 'client',
      timestamp: new Date(Date.now() - 1000 * 60 * 30),
    },
  ],
  '3': [
    {
      id: 'm1',
      content: "Bonjour, j'ai une question concernant ma facture.",
      sender: 'client',
      timestamp: new Date(Date.now() - 1000 * 60 * 60 * 3),
    },
    {
      id: 'm2',
      content: "Bonjour Mme Bernard, je vais vérifier votre dossier immédiatement.",
      sender: 'employee',
      timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2.5),
    },
    {
      id: 'm3',
      content: "Merci pour votre réponse rapide!",
      sender: 'client',
      timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2),
    },
  ],
  '4': [
    {
      id: 'm1',
      content: "J'ai besoin du guide NGBSS pour le nouveau système. Où puis-je le trouver?",
      sender: 'client',
      timestamp: new Date(Date.now() - 1000 * 60 * 60 * 5),
    },
  ],
  '5': [
    {
      id: 'm1',
      content: "Pouvez-vous m'envoyer la convention signée?",
      sender: 'client',
      timestamp: new Date(Date.now() - 1000 * 60 * 60 * 24),
    },
  ],
};

export const mockDocuments: Document[] = [
  {
    id: 'd1',
    title: 'Offre Entreprise Premium 2024',
    category: 'offers',
    content: "Offre complète pour entreprises de 20 à 100 employés. Inclut support 24/7, formation personnalisée, et accès illimité à toutes les fonctionnalités. Tarifs: 49€/utilisateur/mois avec engagement annuel.",
    excerpt: "Offre complète pour entreprises de 20 à 100 employés...",
  },
  {
    id: 'd2',
    title: 'Offre Start-up',
    category: 'offers',
    content: "Package spécial pour les jeunes entreprises. Tarifs réduits pendant les 2 premières années. Support technique inclus.",
    excerpt: "Package spécial pour les jeunes entreprises...",
  },
  {
    id: 'd3',
    title: 'Convention de Partenariat Type A',
    category: 'conventions',
    content: "Convention de partenariat standard pour revendeurs agréés. Conditions de marge: 15% à 25% selon volume. Durée: 12 mois renouvelable.",
    excerpt: "Convention de partenariat standard pour revendeurs...",
  },
  {
    id: 'd4',
    title: 'Convention Distributeur Exclusif',
    category: 'conventions',
    content: "Convention pour distributeurs exclusifs région. Exclusivité géographique garantie. Objectifs de vente trimestriels.",
    excerpt: "Convention pour distributeurs exclusifs région...",
  },
  {
    id: 'd5',
    title: 'Guide NGBSS - Installation',
    category: 'guide-ngbss',
    content: "Guide complet d'installation du système NGBSS. Prérequis techniques, étapes d'installation, configuration initiale, et tests de validation.",
    excerpt: "Guide complet d'installation du système NGBSS...",
  },
  {
    id: 'd6',
    title: 'Guide NGBSS - Configuration Avancée',
    category: 'guide-ngbss',
    content: "Configuration avancée du système NGBSS. Paramètres de sécurité, intégrations API, personnalisation de l'interface.",
    excerpt: "Configuration avancée du système NGBSS...",
  },
  {
    id: 'd7',
    title: 'Conditions Dépôt Vente',
    category: 'depot-vente',
    content: "Conditions générales de dépôt vente. Commission: 10% du prix de vente. Durée maximale: 90 jours. Assurance incluse pour articles > 500€.",
    excerpt: "Conditions générales de dépôt vente. Commission: 10%...",
  },
  {
    id: 'd8',
    title: 'Procédure Dépôt Vente',
    category: 'depot-vente',
    content: "Procédure complète pour déposer un article. Étapes: évaluation, photographie, mise en ligne, gestion des offres, finalisation de la vente.",
    excerpt: "Procédure complète pour déposer un article...",
  },
  {
    id: 'd9',
    title: 'Offre PME Standard',
    category: 'offers',
    content: "Solution adaptée aux PME de 5 à 20 employés. Fonctionnalités essentielles incluses. Support email et téléphone. 29€/utilisateur/mois.",
    excerpt: "Solution adaptée aux PME de 5 à 20 employés...",
  },
  {
    id: 'd10',
    title: 'Guide NGBSS - Dépannage',
    category: 'guide-ngbss',
    content: "Guide de dépannage pour les problèmes courants du système NGBSS. Codes d'erreur, solutions, et procédures de récupération.",
    excerpt: "Guide de dépannage pour les problèmes courants...",
  },
];

export const getCategoryLabel = (category: string): string => {
  const labels: Record<string, string> = {
    'offers': 'Offers',
    'conventions': 'Conventions',
    'guide-ngbss': 'Guide NGBSS',
    'depot-vente': 'Dépôt Vente',
  };
  return labels[category] || category;
};
