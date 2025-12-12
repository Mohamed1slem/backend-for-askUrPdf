export interface Employee {
  id: string;
  name: string;
  email: string;
  role: 'admin' | 'employee';
  avatar?: string;
  createdAt: string;
}

export interface ClientMessage {
  id: string;
  clientName: string;
  clientEmail: string;
  subject: string;
  content: string;
  receivedAt: string;
  status: 'pending' | 'in-progress' | 'replied';
  response?: string;
  attachedDocuments?: Document[];
}

export interface Document {
  id: string;
  title: string;
  summary: string;
  type: 'offers' | 'offers-arabic' | 'conventions' | 'ngbss-guides' | 'depo-vente';
  url: string;
  updatedAt: string;
  relevanceScore?: number;
}

export const employees: Employee[] = [
  {
    id: '1',
    name: 'Ahmed Ben Salem',
    email: 'ahmed.bensalem@company.tn',
    role: 'admin',
    createdAt: '2024-01-15',
  },
  {
    id: '2',
    name: 'Fatma Trabelsi',
    email: 'fatma.trabelsi@company.tn',
    role: 'employee',
    createdAt: '2024-02-20',
  },
  {
    id: '3',
    name: 'Mohamed Gharbi',
    email: 'mohamed.gharbi@company.tn',
    role: 'employee',
    createdAt: '2024-03-10',
  },
  {
    id: '4',
    name: 'Sarra Hammami',
    email: 'sarra.hammami@company.tn',
    role: 'employee',
    createdAt: '2024-04-05',
  },
  {
    id: '5',
    name: 'Youssef Mejri',
    email: 'youssef.mejri@company.tn',
    role: 'employee',
    createdAt: '2024-05-12',
  },
];

export const clientMessages: ClientMessage[] = [
  {
    id: '1',
    clientName: 'Société ABC',
    clientEmail: 'contact@abc-company.tn',
    subject: 'Demande d\'information sur les offres Internet Fibre',
    content: 'Bonjour, nous sommes une entreprise de 50 employés et nous cherchons une solution Internet Fibre pour notre nouveau siège. Pouvez-vous nous envoyer vos offres professionnelles avec les tarifs correspondants? Nous avons besoin d\'un débit minimum de 100 Mbps. Merci de nous contacter rapidement.',
    receivedAt: '2024-12-10T09:30:00',
    status: 'pending',
  },
  {
    id: '2',
    clientName: 'Hotel Mediterranée',
    clientEmail: 'reservation@hotel-med.tn',
    subject: 'Renouvellement contrat téléphonie',
    content: 'Cher partenaire, notre contrat de téléphonie arrive à expiration le mois prochain. Nous souhaiterions connaître les nouvelles conditions et les éventuelles promotions pour un renouvellement. Notre hôtel dispose de 120 lignes téléphoniques.',
    receivedAt: '2024-12-10T11:15:00',
    status: 'in-progress',
  },
  {
    id: '3',
    clientName: 'Clinique Al Amal',
    clientEmail: 'admin@clinique-alamal.tn',
    subject: 'Solution de visioconférence sécurisée',
    content: 'Bonjour, dans le cadre de notre expansion des consultations à distance, nous recherchons une solution de visioconférence sécurisée et conforme aux normes médicales. Pouvez-vous nous proposer une offre adaptée au secteur de la santé?',
    receivedAt: '2024-12-09T14:45:00',
    status: 'pending',
  },
  {
    id: '4',
    clientName: 'Banque du Commerce',
    clientEmail: 'it@banquecommerce.tn',
    subject: 'Mise à niveau infrastructure réseau',
    content: 'Nous planifions une mise à niveau majeure de notre infrastructure réseau pour nos 25 agences. Nous avons besoin d\'une solution SD-WAN avec haute disponibilité. Merci de nous faire parvenir une proposition technique et commerciale.',
    receivedAt: '2024-12-08T16:20:00',
    status: 'replied',
    response: 'Cher client, veuillez trouver ci-joint notre proposition technique pour votre projet SD-WAN...',
  },
];

export const documents: Document[] = [
  {
    id: '1',
    title: 'Offre Fibre Pro 100 Mbps',
    summary: 'Solution Internet Fibre pour entreprises avec débit garanti de 100 Mbps, support 24/7 et SLA 99.9%',
    type: 'offers',
    url: '/docs/fibre-pro-100.pdf',
    updatedAt: '2024-12-01',
  },
  {
    id: '2',
    title: 'Offre Fibre Pro 200 Mbps',
    summary: 'Solution Internet Fibre premium avec débit de 200 Mbps, IP fixe incluse et installation gratuite',
    type: 'offers',
    url: '/docs/fibre-pro-200.pdf',
    updatedAt: '2024-12-01',
  },
  {
    id: '3',
    title: 'عرض الألياف للمؤسسات',
    summary: 'حل الإنترنت بالألياف البصرية للشركات مع ضمان الجودة والدعم الفني على مدار الساعة',
    type: 'offers-arabic',
    url: '/docs/fibre-entreprise-ar.pdf',
    updatedAt: '2024-11-28',
  },
  {
    id: '4',
    title: 'Convention Grandes Entreprises',
    summary: 'Conditions spéciales pour les entreprises de plus de 100 employés incluant remises et services dédiés',
    type: 'conventions',
    url: '/docs/convention-ge.pdf',
    updatedAt: '2024-11-15',
  },
  {
    id: '5',
    title: 'Guide NGBSS - Configuration VoIP',
    summary: 'Guide technique pour la configuration des services VoIP sur la plateforme NGBSS',
    type: 'ngbss-guides',
    url: '/docs/ngbss-voip-guide.pdf',
    updatedAt: '2024-10-20',
  },
  {
    id: '6',
    title: 'Guide Dépôt Vente - Procédures',
    summary: 'Manuel des procédures pour les partenaires du réseau dépôt vente',
    type: 'depo-vente',
    url: '/docs/depo-vente-procedures.pdf',
    updatedAt: '2024-09-30',
  },
  {
    id: '7',
    title: 'Offre SD-WAN Enterprise',
    summary: 'Solution SD-WAN pour interconnexion multi-sites avec haute disponibilité et sécurité avancée',
    type: 'offers',
    url: '/docs/sdwan-enterprise.pdf',
    updatedAt: '2024-12-05',
  },
  {
    id: '8',
    title: 'Pack Téléphonie Business',
    summary: 'Solution de téléphonie IP pour entreprises avec lignes illimitées et fonctionnalités avancées',
    type: 'offers',
    url: '/docs/telephonie-business.pdf',
    updatedAt: '2024-11-20',
  },
];

export const documentTypes = [
  { value: 'all', label: 'Tous les documents' },
  { value: 'offers', label: 'Offres' },
  { value: 'offers-arabic', label: 'Offres en Arabe' },
  { value: 'conventions', label: 'Conventions' },
  { value: 'ngbss-guides', label: 'Guides NGBSS' },
  { value: 'depo-vente', label: 'Dépôt Vente' },
];
