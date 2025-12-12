// import React, { useState, useEffect } from 'react';
// import { Search, FileText, ExternalLink, Calendar, Tag, History, X, Clock } from 'lucide-react';
// // import DashboardLayout from '@/components/layout/DashboardLayout';
// // import { Input } from '@/components/ui/input';
// // import { Button } from '@/components/ui/button';
// // // import { documents, documentTypes, Document } from '@/data/mockData';
// // import {
// //   Select,
// //   SelectContent,
// //   SelectItem,
// //   SelectTrigger,
// //   SelectValue,
// // } from '@/components/ui/select';
// // import { Checkbox } from '@/components/ui/checkbox';
// // import { Label } from '@/components/ui/label';
// // import { toast } from '@/hooks/use-toast';

// interface SearchHistoryItem {
//   id: string;
//   query: string;
//   timestamp: Date;
// }

// const DOC_SEARCH_HISTORY_KEY = 'document-search-history';

// const DocumentSearch: React.FC = () => {
//   const [searchQuery, setSearchQuery] = useState('');
//   const [selectedTypes, setSelectedTypes] = useState<string[]>([]);
//   const [sortBy, setSortBy] = useState('relevance');
//   const [searchHistory, setSearchHistory] = useState<SearchHistoryItem[]>([]);
//   const [showHistory, setShowHistory] = useState(false);

//   // Load search history from localStorage
//   useEffect(() => {
//     const saved = localStorage.getItem(DOC_SEARCH_HISTORY_KEY);
//     if (saved) {
//       const parsed = JSON.parse(saved);
//       setSearchHistory(parsed.map((item: any) => ({ ...item, timestamp: new Date(item.timestamp) })));
//     }
//   }, []);

//   // Save search to history when user searches
//   const saveToHistory = (query: string) => {
//     if (!query.trim()) return;
//     const newItem: SearchHistoryItem = {
//       id: Date.now().toString(),
//       query: query.trim(),
//       timestamp: new Date(),
//     };
//     const updated = [newItem, ...searchHistory.filter(h => h.query !== query)].slice(0, 10);
//     setSearchHistory(updated);
//     localStorage.setItem(DOC_SEARCH_HISTORY_KEY, JSON.stringify(updated));
//   };

//   const removeFromHistory = (id: string) => {
//     const updated = searchHistory.filter(h => h.id !== id);
//     setSearchHistory(updated);
//     localStorage.setItem(DOC_SEARCH_HISTORY_KEY, JSON.stringify(updated));
//   };

//   const clearHistory = () => {
//     setSearchHistory([]);
//     localStorage.removeItem(DOC_SEARCH_HISTORY_KEY);
//     toast({ title: 'Historique effacé', description: 'Votre historique de recherche a été supprimé.' });
//   };

//   const handleHistoryClick = (query: string) => {
//     setSearchQuery(query);
//     setShowHistory(false);
//   };

//   const handleSearch = (value: string) => {
//     setSearchQuery(value);
//     if (value.trim().length >= 3) {
//       saveToHistory(value);
//     }
//   };

//   const filteredDocs = documents.filter((doc) => {
//     const matchesSearch =
//       searchQuery === '' ||
//       doc.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
//       doc.summary.toLowerCase().includes(searchQuery.toLowerCase());
//     const matchesType = selectedTypes.length === 0 || selectedTypes.includes(doc.type);
//     return matchesSearch && matchesType;
//   });

//   const sortedDocs = [...filteredDocs].sort((a, b) => {
//     if (sortBy === 'date') {
//       return new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime();
//     }
//     return 0;
//   });

//   const handleTypeToggle = (type: string) => {
//     setSelectedTypes((prev) =>
//       prev.includes(type) ? prev.filter((t) => t !== type) : [...prev, type]
//     );
//   };

//   const getTypeColor = (type: string) => {
//     switch (type) {
//       case 'offers':
//         return 'bg-primary/10 text-primary';
//       case 'offers-arabic':
//         return 'bg-accent/10 text-accent';
//       case 'conventions':
//         return 'bg-success/10 text-success';
//       case 'ngbss-guides':
//         return 'bg-warning/10 text-warning';
//       case 'depo-vente':
//         return 'bg-destructive/10 text-destructive';
//       default:
//         return 'bg-muted text-muted-foreground';
//     }
//   };

//   return (
//     <DashboardLayout>
//       <div className="animate-fade-in">
//         <div className="mb-8 flex items-start justify-between">
//           <div>
//             <h1 className="text-2xl font-bold text-foreground mb-2">Recherche Documents</h1>
//             <p className="text-muted-foreground">
//               Trouvez rapidement les offres et documents pertinents pour vos clients
//             </p>
//           </div>
//           <Button
//             variant="outline"
//             size="sm"
//             onClick={() => setShowHistory(!showHistory)}
//             className="gap-2"
//           >
//             <History className="w-4 h-4" />
//             Historique
//           </Button>
//         </div>

//         {/* Search History Panel */}
//         {showHistory && searchHistory.length > 0 && (
//           <div className="mb-6 card-elevated p-4 animate-slide-up">
//             <div className="flex items-center justify-between mb-3">
//               <h3 className="font-semibold text-sm text-foreground">Recherches récentes</h3>
//               <Button variant="ghost" size="sm" onClick={clearHistory} className="text-xs text-muted-foreground">
//                 Tout effacer
//               </Button>
//             </div>
//             <div className="flex flex-wrap gap-2">
//               {searchHistory.map((item) => (
//                 <div
//                   key={item.id}
//                   className="flex items-center gap-1 px-3 py-1.5 rounded-full bg-muted hover:bg-muted/80 cursor-pointer group"
//                   onClick={() => handleHistoryClick(item.query)}
//                 >
//                   <Clock className="w-3 h-3 text-muted-foreground" />
//                   <span className="text-sm text-foreground">{item.query}</span>
//                   <button
//                     className="ml-1 opacity-0 group-hover:opacity-100 transition-opacity"
//                     onClick={(e) => {
//                       e.stopPropagation();
//                       removeFromHistory(item.id);
//                     }}
//                   >
//                     <X className="w-3 h-3 text-muted-foreground hover:text-foreground" />
//                   </button>
//                 </div>
//               ))}
//             </div>
//           </div>
//         )}

//         {showHistory && searchHistory.length === 0 && (
//           <div className="mb-6 card-elevated p-6 text-center animate-slide-up">
//             <Clock className="w-8 h-8 text-muted-foreground mx-auto mb-2" />
//             <p className="text-sm text-muted-foreground">Aucun historique de recherche</p>
//           </div>
//         )}

//         <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
//           {/* Filters Sidebar */}
//           <div className="lg:col-span-1">
//             <div className="card-elevated p-6 sticky top-24">
//               <h3 className="font-semibold text-foreground mb-4">Filtres</h3>

//               <div className="space-y-4">
//                 <div>
//                   <Label className="text-sm text-muted-foreground mb-2 block">
//                     Type de document
//                   </Label>
//                   <div className="space-y-2">
//                     {documentTypes.slice(1).map((type) => (
//                       <div key={type.value} className="flex items-center gap-2">
//                         <Checkbox
//                           id={type.value}
//                           checked={selectedTypes.includes(type.value)}
//                           onCheckedChange={() => handleTypeToggle(type.value)}
//                         />
//                         <label
//                           htmlFor={type.value}
//                           className="text-sm text-foreground cursor-pointer"
//                         >
//                           {type.label}
//                         </label>
//                       </div>
//                     ))}
//                   </div>
//                 </div>

//                 <div>
//                   <Label className="text-sm text-muted-foreground mb-2 block">Trier par</Label>
//                   <Select value={sortBy} onValueChange={setSortBy}>
//                     <SelectTrigger>
//                       <SelectValue />
//                     </SelectTrigger>
//                     <SelectContent>
//                       <SelectItem value="relevance">Pertinence</SelectItem>
//                       <SelectItem value="date">Date de mise à jour</SelectItem>
//                     </SelectContent>
//                   </Select>
//                 </div>

//                 {selectedTypes.length > 0 && (
//                   <Button
//                     variant="outline"
//                     size="sm"
//                     onClick={() => setSelectedTypes([])}
//                     className="w-full"
//                   >
//                     Effacer les filtres
//                   </Button>
//                 )}
//               </div>
//             </div>
//           </div>

//           {/* Search Results */}
//           <div className="lg:col-span-3 space-y-6">
//             {/* Search Bar */}
//             <div className="card-elevated p-4">
//               <div className="relative">
//                 <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
//                 <Input
//                   placeholder="Rechercher par mots-clés, titre, contenu..."
//                   value={searchQuery}
//                   onChange={(e) => handleSearch(e.target.value)}
//                   className="pl-12 h-12 text-base"
//                 />
//               </div>
//             </div>

//             {/* Results Count */}
//             <div className="flex items-center justify-between">
//               <p className="text-sm text-muted-foreground">
//                 {sortedDocs.length} document{sortedDocs.length > 1 ? 's' : ''} trouvé
//                 {sortedDocs.length > 1 ? 's' : ''}
//               </p>
//             </div>

//             {/* Document Cards */}
//             <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
//               {sortedDocs.map((doc, index) => (
//                 <div
//                   key={doc.id}
//                   className="card-interactive p-5 animate-slide-up"
//                   style={{ animationDelay: `${index * 0.05}s` }}
//                 >
//                   <div className="flex items-start gap-4">
//                     <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center flex-shrink-0">
//                       <FileText className="w-6 h-6 text-primary" />
//                     </div>
//                     <div className="flex-1 min-w-0">
//                       <h3 className="font-semibold text-foreground mb-1 line-clamp-1">
//                         {doc.title}
//                       </h3>
//                       <p className="text-sm text-muted-foreground line-clamp-2 mb-3">
//                         {doc.summary}
//                       </p>
//                       <div className="flex items-center gap-3 flex-wrap">
//                         <span className={`text-xs px-2 py-1 rounded-full ${getTypeColor(doc.type)}`}>
//                           <Tag className="w-3 h-3 inline mr-1" />
//                           {documentTypes.find((t) => t.value === doc.type)?.label}
//                         </span>
//                         <span className="text-xs text-muted-foreground flex items-center gap-1">
//                           <Calendar className="w-3 h-3" />
//                           {new Date(doc.updatedAt).toLocaleDateString('fr-FR')}
//                         </span>
//                       </div>
//                     </div>
//                   </div>
//                   <div className="mt-4 pt-4 border-t border-border">
//                     <Button variant="outline" size="sm" className="w-full gap-2">
//                       <ExternalLink className="w-4 h-4" />
//                       Ouvrir le document
//                     </Button>
//                   </div>
//                 </div>
//               ))}
//             </div>

//             {sortedDocs.length === 0 && (
//               <div className="card-elevated p-12 text-center">
//                 <FileText className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
//                 <h3 className="font-semibold text-foreground mb-2">Aucun document trouvé</h3>
//                 <p className="text-sm text-muted-foreground">
//                   Essayez de modifier vos critères de recherche
//                 </p>
//               </div>
//             )}
//           </div>
//         </div>
//       </div>
//     </DashboardLayout>
//   );
// };

// export default DocumentSearch;
