// import React, { useState } from 'react';
// import { ChevronDown, ChevronUp, Send, FileSearch, Bot, Paperclip, X, Check } from 'lucide-react';
// // import DashboardLayout from '@/components/layout/DashboardLayout';
// // import { Button } from '@/components/ui/button';
// // import { Textarea } from '@/components/ui/textarea';
// // import { Input } from '@/components/ui/input';
// // import { clientMessages as initialMessages, documents, documentTypes, ClientMessage, Document } from '@/data/mockData';
// // import { toast } from '@/hooks/use-toast';
// // import {
// //   Select,
// //   SelectContent,
// //   SelectItem,
// //   SelectTrigger,
// //   SelectValue,
// // } from '@/components/ui/select';

// const ClientMessages: React.FC = () => {
//   const [messages, setMessages] = useState<ClientMessage[]>(initialMessages);
//   const [expandedId, setExpandedId] = useState<string | null>(null);
//   const [responseText, setResponseText] = useState('');
//   const [selectedDocs, setSelectedDocs] = useState<Document[]>([]);
//   const [showDocSearch, setShowDocSearch] = useState(false);
//   const [showChatbot, setShowChatbot] = useState(false);
//   const [docSearchQuery, setDocSearchQuery] = useState('');
//   const [docTypeFilter, setDocTypeFilter] = useState('all');
//   const [aiSuggestion, setAiSuggestion] = useState<string | null>(null);
//   const [isGenerating, setIsGenerating] = useState(false);

//   const expandedMessage = messages.find((m) => m.id === expandedId);

//   const filteredDocs = documents.filter((doc) => {
//     const matchesSearch = doc.title.toLowerCase().includes(docSearchQuery.toLowerCase()) ||
//       doc.summary.toLowerCase().includes(docSearchQuery.toLowerCase());
//     const matchesType = docTypeFilter === 'all' || doc.type === docTypeFilter;
//     return matchesSearch && matchesType;
//   });

//   const handleToggleExpand = (id: string) => {
//     if (expandedId === id) {
//       setExpandedId(null);
//       resetResponseState();
//     } else {
//       setExpandedId(id);
//       resetResponseState();
//     }
//   };

//   const resetResponseState = () => {
//     setResponseText('');
//     setSelectedDocs([]);
//     setShowDocSearch(false);
//     setShowChatbot(false);
//     setAiSuggestion(null);
//   };

//   const handleSelectDoc = (doc: Document) => {
//     if (selectedDocs.find((d) => d.id === doc.id)) {
//       setSelectedDocs(selectedDocs.filter((d) => d.id !== doc.id));
//     } else {
//       setSelectedDocs([...selectedDocs, doc]);
//     }
//   };

//   const handleGenerateAI = async () => {
//     setIsGenerating(true);
//     // Simulate AI generation
//     await new Promise((resolve) => setTimeout(resolve, 1500));
    
//     const suggestion = `Cher client,

// Nous vous remercions pour votre intérêt pour nos services. Suite à votre demande, nous avons le plaisir de vous informer que nous disposons de plusieurs solutions adaptées à vos besoins.

// Vous trouverez ci-joint les documents suivants qui correspondent à votre demande :
// - Offre Fibre Pro avec débit garanti
// - Convention Grandes Entreprises avec conditions préférentielles

// Notre équipe commerciale reste à votre disposition pour toute information complémentaire ou pour organiser une démonstration.

// Cordialement,
// L'équipe Smart Offer Finder`;

//     setAiSuggestion(suggestion);
//     setIsGenerating(false);
//   };

//   const handleAcceptAI = () => {
//     setResponseText(aiSuggestion || '');
//     setAiSuggestion(null);
//     setShowChatbot(false);
//     toast({
//       title: 'Suggestion acceptée',
//       description: 'La réponse IA a été ajoutée à votre message.',
//     });
//   };

//   const handleSendResponse = () => {
//     if (!expandedId || !responseText.trim()) return;

//     setMessages(
//       messages.map((msg) =>
//         msg.id === expandedId
//           ? {
//               ...msg,
//               status: 'replied' as const,
//               response: responseText,
//               attachedDocuments: selectedDocs,
//             }
//           : msg
//       )
//     );

//     toast({
//       title: 'Réponse envoyée',
//       description: 'Votre réponse a été envoyée au client avec succès.',
//     });

//     setExpandedId(null);
//     resetResponseState();
//   };

//   return (
//     <DashboardLayout>
//       <div className="animate-fade-in">
//         <div className="mb-8">
//           <h1 className="text-2xl font-bold text-foreground mb-2">Messages Clients</h1>
//           <p className="text-muted-foreground">Gérez les demandes clients et envoyez des réponses personnalisées</p>
//         </div>

//         <div className="space-y-4">
//           {messages.map((message) => (
//             <div
//               key={message.id}
//               className={`card-elevated overflow-hidden transition-all duration-300 ${
//                 expandedId === message.id ? 'ring-2 ring-primary/20' : ''
//               }`}
//             >
//               {/* Message Header */}
//               <button
//                 onClick={() => handleToggleExpand(message.id)}
//                 className="w-full p-4 flex items-center gap-4 hover:bg-muted/30 transition-colors"
//               >
//                 <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
//                   <span className="text-sm font-semibold text-primary">
//                     {message.clientName.split(' ').map((n) => n[0]).join('').slice(0, 2)}
//                   </span>
//                 </div>
//                 <div className="flex-1 text-left min-w-0">
//                   <div className="flex items-center gap-2 mb-1">
//                     <p className="font-medium text-foreground">{message.clientName}</p>
//                     <span
//                       className={`text-xs px-2 py-0.5 rounded-full ${
//                         message.status === 'pending'
//                           ? 'bg-warning/10 text-warning'
//                           : message.status === 'replied'
//                           ? 'bg-success/10 text-success'
//                           : 'bg-primary/10 text-primary'
//                       }`}
//                     >
//                       {message.status === 'pending'
//                         ? 'En attente'
//                         : message.status === 'replied'
//                         ? 'Répondu'
//                         : 'En cours'}
//                     </span>
//                   </div>
//                   <p className="text-sm text-muted-foreground truncate">{message.subject}</p>
//                 </div>
//                 <span className="text-xs text-muted-foreground flex-shrink-0">
//                   {new Date(message.receivedAt).toLocaleDateString('fr-FR', {
//                     day: 'numeric',
//                     month: 'short',
//                     hour: '2-digit',
//                     minute: '2-digit',
//                   })}
//                 </span>
//                 {expandedId === message.id ? (
//                   <ChevronUp className="w-5 h-5 text-muted-foreground" />
//                 ) : (
//                   <ChevronDown className="w-5 h-5 text-muted-foreground" />
//                 )}
//               </button>

//               {/* Expanded Content */}
//               {expandedId === message.id && (
//                 <div className="border-t border-border animate-slide-up">
//                   {/* Message Content */}
//                   <div className="p-6 bg-muted/20">
//                     <h4 className="text-sm font-medium text-muted-foreground mb-2">Message du client :</h4>
//                     <p className="text-foreground whitespace-pre-wrap">{message.content}</p>
//                     <p className="text-xs text-muted-foreground mt-3">
//                       De : {message.clientEmail}
//                     </p>
//                   </div>

//                   {/* Previous Response */}
//                   {message.response && (
//                     <div className="p-6 bg-success/5 border-t border-border">
//                       <h4 className="text-sm font-medium text-success mb-2">Réponse envoyée :</h4>
//                       <p className="text-foreground whitespace-pre-wrap">{message.response}</p>
//                     </div>
//                   )}

//                   {/* Response Tools */}
//                   {message.status !== 'replied' && (
//                     <div className="p-6 space-y-4">
//                       {/* Tool Buttons */}
//                       <div className="flex gap-3">
//                         <Button
//                           variant={showDocSearch ? 'default' : 'outline'}
//                           onClick={() => {
//                             setShowDocSearch(!showDocSearch);
//                             setShowChatbot(false);
//                           }}
//                           className="gap-2"
//                         >
//                           <FileSearch className="w-4 h-4" />
//                           Rechercher Documents
//                         </Button>
//                         <Button
//                           variant={showChatbot ? 'default' : 'outline'}
//                           onClick={() => {
//                             setShowChatbot(!showChatbot);
//                             setShowDocSearch(false);
//                           }}
//                           className="gap-2"
//                         >
//                           <Bot className="w-4 h-4" />
//                           Assistant IA
//                         </Button>
//                       </div>

//                       {/* Document Search */}
//                       {showDocSearch && (
//                         <div className="card-elevated p-4 space-y-4 animate-scale-in">
//                           <div className="flex gap-3">
//                             <Input
//                               placeholder="Rechercher des documents..."
//                               value={docSearchQuery}
//                               onChange={(e) => setDocSearchQuery(e.target.value)}
//                               className="flex-1"
//                             />
//                             <Select value={docTypeFilter} onValueChange={setDocTypeFilter}>
//                               <SelectTrigger className="w-48">
//                                 <SelectValue placeholder="Type de document" />
//                               </SelectTrigger>
//                               <SelectContent>
//                                 {documentTypes.map((type) => (
//                                   <SelectItem key={type.value} value={type.value}>
//                                     {type.label}
//                                   </SelectItem>
//                                 ))}
//                               </SelectContent>
//                             </Select>
//                           </div>

//                           <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-h-64 overflow-y-auto">
//                             {filteredDocs.slice(0, 4).map((doc) => (
//                               <button
//                                 key={doc.id}
//                                 onClick={() => handleSelectDoc(doc)}
//                                 className={`p-3 rounded-lg border text-left transition-all ${
//                                   selectedDocs.find((d) => d.id === doc.id)
//                                     ? 'border-primary bg-primary/5'
//                                     : 'border-border hover:border-primary/50'
//                                 }`}
//                               >
//                                 <div className="flex items-start gap-2">
//                                   <div
//                                     className={`w-5 h-5 rounded border flex items-center justify-center flex-shrink-0 mt-0.5 ${
//                                       selectedDocs.find((d) => d.id === doc.id)
//                                         ? 'bg-primary border-primary'
//                                         : 'border-border'
//                                     }`}
//                                   >
//                                     {selectedDocs.find((d) => d.id === doc.id) && (
//                                       <Check className="w-3 h-3 text-primary-foreground" />
//                                     )}
//                                   </div>
//                                   <div className="flex-1 min-w-0">
//                                     <p className="font-medium text-sm text-foreground truncate">
//                                       {doc.title}
//                                     </p>
//                                     <p className="text-xs text-muted-foreground line-clamp-2 mt-1">
//                                       {doc.summary}
//                                     </p>
//                                     <span className="text-xs text-primary mt-1 inline-block">
//                                       {documentTypes.find((t) => t.value === doc.type)?.label}
//                                     </span>
//                                   </div>
//                                 </div>
//                               </button>
//                             ))}
//                           </div>
//                         </div>
//                       )}

//                       {/* AI Chatbot */}
//                       {showChatbot && (
//                         <div className="card-elevated p-4 space-y-4 animate-scale-in">
//                           <p className="text-sm text-muted-foreground">
//                             L'assistant IA va générer une réponse basée sur le message du client et les documents pertinents.
//                           </p>
                          
//                           {!aiSuggestion && (
//                             <Button onClick={handleGenerateAI} disabled={isGenerating} className="gap-2">
//                               {isGenerating ? (
//                                 <>
//                                   <span className="w-4 h-4 border-2 border-primary-foreground/30 border-t-primary-foreground rounded-full animate-spin"></span>
//                                   Génération en cours...
//                                 </>
//                               ) : (
//                                 <>
//                                   <Bot className="w-4 h-4" />
//                                   Générer une suggestion
//                                 </>
//                               )}
//                             </Button>
//                           )}

//                           {aiSuggestion && (
//                             <div className="space-y-3">
//                               <div className="p-4 bg-primary/5 rounded-lg border border-primary/20">
//                                 <p className="text-sm text-foreground whitespace-pre-wrap">{aiSuggestion}</p>
//                               </div>
//                               <div className="flex gap-2">
//                                 <Button onClick={handleAcceptAI} variant="success" className="gap-2">
//                                   <Check className="w-4 h-4" />
//                                   Accepter
//                                 </Button>
//                                 <Button
//                                   onClick={() => setAiSuggestion(null)}
//                                   variant="outline"
//                                   className="gap-2"
//                                 >
//                                   <X className="w-4 h-4" />
//                                   Rejeter
//                                 </Button>
//                               </div>
//                             </div>
//                           )}
//                         </div>
//                       )}

//                       {/* Selected Documents */}
//                       {selectedDocs.length > 0 && (
//                         <div className="flex flex-wrap gap-2">
//                           {selectedDocs.map((doc) => (
//                             <span
//                               key={doc.id}
//                               className="inline-flex items-center gap-1 px-3 py-1 bg-primary/10 text-primary text-sm rounded-full"
//                             >
//                               <Paperclip className="w-3 h-3" />
//                               {doc.title}
//                               <button
//                                 onClick={() => handleSelectDoc(doc)}
//                                 className="ml-1 hover:text-destructive"
//                               >
//                                 <X className="w-3 h-3" />
//                               </button>
//                             </span>
//                           ))}
//                         </div>
//                       )}

//                       {/* Response Textarea */}
//                       <Textarea
//                         placeholder="Écrivez votre réponse ici..."
//                         value={responseText}
//                         onChange={(e) => setResponseText(e.target.value)}
//                         rows={5}
//                         className="resize-none"
//                       />

//                       {/* Send Button */}
//                       <div className="flex justify-end">
//                         <Button
//                           onClick={handleSendResponse}
//                           disabled={!responseText.trim()}
//                           className="gap-2"
//                         >
//                           <Send className="w-4 h-4" />
//                           Envoyer la réponse
//                         </Button>
//                       </div>
//                     </div>
//                   )}
//                 </div>
//               )}
//             </div>
//           ))}
//         </div>
//       </div>
//     </DashboardLayout>
//   );
// };

// export default ClientMessages;
