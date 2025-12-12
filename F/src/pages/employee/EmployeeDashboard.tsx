// import React from 'react';
// import { MessageSquare, FileSearch, Bot, Clock } from 'lucide-react';
// import { Link } from 'react-router-dom';
// // import DashboardLayout from '@/components/layout/DashboardLayout';
// // import { clientMessages, documents } from '@/data/mockData';
// import { useAuth } from '@/contexts/AuthContext';

// const EmployeeDashboard: React.FC = () => {
//   const { user } = useAuth();
  
//   const stats = [
//     {
//       label: 'Messages en attente',
//       value: clientMessages.filter(m => m.status === 'pending').length,
//       icon: MessageSquare,
//       color: 'bg-warning/10 text-warning',
//       link: '/employee/messages',
//     },
//     {
//       label: 'En cours de traitement',
//       value: clientMessages.filter(m => m.status === 'in-progress').length,
//       icon: Clock,
//       color: 'bg-primary/10 text-primary',
//       link: '/employee/messages',
//     },
//     {
//       label: 'Documents disponibles',
//       value: documents.length,
//       icon: FileSearch,
//       color: 'bg-success/10 text-success',
//       link: '/employee/documents',
//     },
//     {
//       label: 'Requêtes IA ce mois',
//       value: 47,
//       icon: Bot,
//       color: 'bg-accent/10 text-accent',
//       link: '/employee/chatbot',
//     },
//   ];

//   return (
//     <DashboardLayout>
//       <div className="animate-fade-in">
//         <div className="mb-8">
//           <h1 className="text-2xl font-bold text-foreground mb-2">
//             Bienvenue, {user?.name?.split(' ')[0]}
//           </h1>
//           <p className="text-muted-foreground">
//             Votre espace de travail pour gérer les demandes clients
//           </p>
//         </div>

//         {/* Stats Grid */}
//         <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
//           {stats.map((stat, index) => (
//             <Link
//               key={stat.label}
//               to={stat.link}
//               className="card-interactive p-6 animate-slide-up"
//               style={{ animationDelay: `${index * 0.1}s` }}
//             >
//               <div className="flex items-start justify-between mb-4">
//                 <div className={`w-12 h-12 rounded-xl ${stat.color} flex items-center justify-center`}>
//                   <stat.icon className="w-6 h-6" />
//                 </div>
//               </div>
//               <div className="text-3xl font-bold text-foreground mb-1">{stat.value}</div>
//               <div className="text-sm text-muted-foreground">{stat.label}</div>
//             </Link>
//           ))}
//         </div>

//         {/* Quick Actions */}
//         <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
//           <Link
//             to="/employee/messages"
//             className="card-interactive p-6 flex items-center gap-4"
//           >
//             <div className="w-14 h-14 rounded-xl bg-primary/10 flex items-center justify-center">
//               <MessageSquare className="w-7 h-7 text-primary" />
//             </div>
//             <div>
//               <h3 className="font-semibold text-foreground mb-1">Messages Clients</h3>
//               <p className="text-sm text-muted-foreground">Consultez et répondez aux demandes</p>
//             </div>
//           </Link>

//           <Link
//             to="/employee/documents"
//             className="card-interactive p-6 flex items-center gap-4"
//           >
//             <div className="w-14 h-14 rounded-xl bg-success/10 flex items-center justify-center">
//               <FileSearch className="w-7 h-7 text-success" />
//             </div>
//             <div>
//               <h3 className="font-semibold text-foreground mb-1">Recherche Documents</h3>
//               <p className="text-sm text-muted-foreground">Trouvez les offres pertinentes</p>
//             </div>
//           </Link>

//           <Link
//             to="/employee/chatbot"
//             className="card-interactive p-6 flex items-center gap-4"
//           >
//             <div className="w-14 h-14 rounded-xl bg-accent/10 flex items-center justify-center">
//               <Bot className="w-7 h-7 text-accent" />
//             </div>
//             <div>
//               <h3 className="font-semibold text-foreground mb-1">Assistant IA</h3>
//               <p className="text-sm text-muted-foreground">Générez des réponses automatiques</p>
//             </div>
//           </Link>
//         </div>

//         {/* Recent Messages */}
//         <div className="card-elevated p-6">
//           <div className="flex items-center justify-between mb-4">
//             <h2 className="text-lg font-semibold text-foreground">Messages Récents</h2>
//             <Link to="/employee/messages" className="text-sm text-primary hover:underline">
//               Voir tout
//             </Link>
//           </div>
//           <div className="space-y-3">
//             {clientMessages.slice(0, 3).map((message) => (
//               <div
//                 key={message.id}
//                 className="flex items-center gap-4 p-4 rounded-lg bg-muted/30 hover:bg-muted/50 transition-colors"
//               >
//                 <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
//                   <span className="text-sm font-semibold text-primary">
//                     {message.clientName.split(' ').map(n => n[0]).join('').slice(0, 2)}
//                   </span>
//                 </div>
//                 <div className="flex-1 min-w-0">
//                   <div className="flex items-center gap-2 mb-1">
//                     <p className="font-medium text-foreground truncate">{message.clientName}</p>
//                     <span className={`text-xs px-2 py-0.5 rounded-full flex-shrink-0 ${
//                       message.status === 'pending'
//                         ? 'bg-warning/10 text-warning'
//                         : message.status === 'replied'
//                         ? 'bg-success/10 text-success'
//                         : 'bg-primary/10 text-primary'
//                     }`}>
//                       {message.status === 'pending' ? 'En attente' :
//                        message.status === 'replied' ? 'Répondu' : 'En cours'}
//                     </span>
//                   </div>
//                   <p className="text-sm text-muted-foreground truncate">{message.subject}</p>
//                 </div>
//                 <span className="text-xs text-muted-foreground flex-shrink-0">
//                   {new Date(message.receivedAt).toLocaleDateString('fr-FR')}
//                 </span>
//               </div>
//             ))}
//           </div>
//         </div>
//       </div>
//     </DashboardLayout>
//   );
// };

// export default EmployeeDashboard;
