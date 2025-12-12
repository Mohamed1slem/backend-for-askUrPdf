// import React, { useState } from 'react';
// import { Plus, Search, Pencil, Trash2, X } from 'lucide-react';
// import DashboardLayout from '@/components/layout/DashboardLayout';
// import { Button } from '@/components/ui/button';
// import { Input } from '@/components/ui/input';
// import { Label } from '@/components/ui/label';
// import { employees as initialEmployees, Employee } from '@/data/mockData';
// import { toast } from '@/hooks/use-toast';
// import {
//   Dialog,
//   DialogContent,
//   DialogHeader,
//   DialogTitle,
// } from '@/components/ui/dialog';
// import {
//   Select,
//   SelectContent,
//   SelectItem,
//   SelectTrigger,
//   SelectValue,
// } from '@/components/ui/select';

// const EmployeeManagement: React.FC = () => {
//   const [employees, setEmployees] = useState<Employee[]>(initialEmployees);
//   const [searchQuery, setSearchQuery] = useState('');
//   const [isModalOpen, setIsModalOpen] = useState(false);
//   const [editingEmployee, setEditingEmployee] = useState<Employee | null>(null);
//   const [formData, setFormData] = useState({
//     name: '',
//     email: '',
//     role: 'employee' as 'admin' | 'employee',
//     password: '',
//   });

//   const filteredEmployees = employees.filter(
//     (emp) =>
//       emp.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
//       emp.email.toLowerCase().includes(searchQuery.toLowerCase())
//   );

//   const handleOpenModal = (employee?: Employee) => {
//     if (employee) {
//       setEditingEmployee(employee);
//       setFormData({
//         name: employee.name,
//         email: employee.email,
//         role: employee.role,
//         password: '',
//       });
//     } else {
//       setEditingEmployee(null);
//       setFormData({ name: '', email: '', role: 'employee', password: '' });
//     }
//     setIsModalOpen(true);
//   };

//   const handleCloseModal = () => {
//     setIsModalOpen(false);
//     setEditingEmployee(null);
//     setFormData({ name: '', email: '', role: 'employee', password: '' });
//   };

//   const handleSubmit = (e: React.FormEvent) => {
//     e.preventDefault();

//     if (editingEmployee) {
//       setEmployees(
//         employees.map((emp) =>
//           emp.id === editingEmployee.id
//             ? { ...emp, name: formData.name, email: formData.email, role: formData.role }
//             : emp
//         )
//       );
//       toast({
//         title: 'Employé modifié',
//         description: `${formData.name} a été mis à jour avec succès.`,
//       });
//     } else {
//       const newEmployee: Employee = {
//         id: Date.now().toString(),
//         name: formData.name,
//         email: formData.email,
//         role: formData.role,
//         createdAt: new Date().toISOString().split('T')[0],
//       };
//       setEmployees([...employees, newEmployee]);
//       toast({
//         title: 'Employé ajouté',
//         description: `${formData.name} a été ajouté avec succès.`,
//       });
//     }

//     handleCloseModal();
//   };

//   const handleDelete = (employee: Employee) => {
//     setEmployees(employees.filter((emp) => emp.id !== employee.id));
//     toast({
//       title: 'Employé supprimé',
//       description: `${employee.name} a été supprimé.`,
//       variant: 'destructive',
//     });
//   };

//   return (
//     <DashboardLayout>
//       <div className="animate-fade-in">
//         <div className="flex items-center justify-between mb-8">
//           <div>
//             <h1 className="text-2xl font-bold text-foreground mb-2">Gestion des Employés</h1>
//             <p className="text-muted-foreground">Gérez les comptes des employés de la plateforme</p>
//           </div>
//           <Button onClick={() => handleOpenModal()} className="gap-2">
//             <Plus className="w-4 h-4" />
//             Ajouter un employé
//           </Button>
//         </div>

//         {/* Search Bar */}
//         <div className="card-elevated p-4 mb-6">
//           <div className="relative max-w-md">
//             <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
//             <Input
//               placeholder="Rechercher par nom ou email..."
//               value={searchQuery}
//               onChange={(e) => setSearchQuery(e.target.value)}
//               className="pl-10"
//             />
//           </div>
//         </div>

//         {/* Employee Table */}
//         <div className="card-elevated overflow-hidden">
//           <div className="overflow-x-auto">
//             <table className="w-full">
//               <thead>
//                 <tr className="border-b border-border bg-muted/50">
//                   <th className="text-left p-4 text-sm font-medium text-muted-foreground">Nom</th>
//                   <th className="text-left p-4 text-sm font-medium text-muted-foreground">Email</th>
//                   <th className="text-left p-4 text-sm font-medium text-muted-foreground">Rôle</th>
//                   <th className="text-left p-4 text-sm font-medium text-muted-foreground">Date d'ajout</th>
//                   <th className="text-right p-4 text-sm font-medium text-muted-foreground">Actions</th>
//                 </tr>
//               </thead>
//               <tbody>
//                 {filteredEmployees.map((employee, index) => (
//                   <tr
//                     key={employee.id}
//                     className="border-b border-border last:border-0 hover:bg-muted/30 transition-colors animate-slide-up"
//                     style={{ animationDelay: `${index * 0.05}s` }}
//                   >
//                     <td className="p-4">
//                       <div className="flex items-center gap-3">
//                         <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
//                           <span className="text-sm font-semibold text-primary">
//                             {employee.name.split(' ').map((n) => n[0]).join('')}
//                           </span>
//                         </div>
//                         <span className="font-medium text-foreground">{employee.name}</span>
//                       </div>
//                     </td>
//                     <td className="p-4 text-muted-foreground">{employee.email}</td>
//                     <td className="p-4">
//                       <span
//                         className={`text-xs px-3 py-1 rounded-full font-medium ${
//                           employee.role === 'admin'
//                             ? 'bg-primary/10 text-primary'
//                             : 'bg-muted text-muted-foreground'
//                         }`}
//                       >
//                         {employee.role === 'admin' ? 'Administrateur' : 'Employé'}
//                       </span>
//                     </td>
//                     <td className="p-4 text-muted-foreground">{employee.createdAt}</td>
//                     <td className="p-4">
//                       <div className="flex items-center justify-end gap-2">
//                         <Button
//                           variant="ghost"
//                           size="icon"
//                           onClick={() => handleOpenModal(employee)}
//                           className="text-muted-foreground hover:text-primary"
//                         >
//                           <Pencil className="w-4 h-4" />
//                         </Button>
//                         <Button
//                           variant="ghost"
//                           size="icon"
//                           onClick={() => handleDelete(employee)}
//                           className="text-muted-foreground hover:text-destructive"
//                         >
//                           <Trash2 className="w-4 h-4" />
//                         </Button>
//                       </div>
//                     </td>
//                   </tr>
//                 ))}
//               </tbody>
//             </table>
//           </div>

//           {filteredEmployees.length === 0 && (
//             <div className="p-8 text-center text-muted-foreground">
//               Aucun employé trouvé
//             </div>
//           )}
//         </div>

//         {/* Add/Edit Modal */}
//         <Dialog open={isModalOpen} onOpenChange={setIsModalOpen}>
//           <DialogContent className="sm:max-w-md">
//             <DialogHeader>
//               <DialogTitle>
//                 {editingEmployee ? 'Modifier l\'employé' : 'Ajouter un employé'}
//               </DialogTitle>
//             </DialogHeader>
//             <form onSubmit={handleSubmit} className="space-y-4 mt-4">
//               <div className="space-y-2">
//                 <Label htmlFor="name">Nom complet</Label>
//                 <Input
//                   id="name"
//                   value={formData.name}
//                   onChange={(e) => setFormData({ ...formData, name: e.target.value })}
//                   placeholder="Nom et prénom"
//                   required
//                 />
//               </div>
//               <div className="space-y-2">
//                 <Label htmlFor="email">Email</Label>
//                 <Input
//                   id="email"
//                   type="email"
//                   value={formData.email}
//                   onChange={(e) => setFormData({ ...formData, email: e.target.value })}
//                   placeholder="email@company.tn"
//                   required
//                 />
//               </div>
//               <div className="space-y-2">
//                 <Label htmlFor="role">Rôle</Label>
//                 <Select
//                   value={formData.role}
//                   onValueChange={(value: 'admin' | 'employee') =>
//                     setFormData({ ...formData, role: value })
//                   }
//                 >
//                   <SelectTrigger>
//                     <SelectValue placeholder="Sélectionner un rôle" />
//                   </SelectTrigger>
//                   <SelectContent>
//                     <SelectItem value="employee">Employé</SelectItem>
//                     <SelectItem value="admin">Administrateur</SelectItem>
//                   </SelectContent>
//                 </Select>
//               </div>
//               {!editingEmployee && (
//                 <div className="space-y-2">
//                   <Label htmlFor="password">Mot de passe</Label>
//                   <Input
//                     id="password"
//                     type="password"
//                     value={formData.password}
//                     onChange={(e) => setFormData({ ...formData, password: e.target.value })}
//                     placeholder="••••••••"
//                     required={!editingEmployee}
//                   />
//                 </div>
//               )}
//               <div className="flex justify-end gap-3 pt-4">
//                 <Button type="button" variant="outline" onClick={handleCloseModal}>
//                   Annuler
//                 </Button>
//                 <Button type="submit">
//                   {editingEmployee ? 'Enregistrer' : 'Ajouter'}
//                 </Button>
//               </div>
//             </form>
//           </DialogContent>
//         </Dialog>
//       </div>
//     </DashboardLayout>
//   );
// };

// export default EmployeeManagement;
