import React from 'react';
import { Users, MessageSquare, FileText, TrendingUp } from 'lucide-react';
import DashboardLayout from '@/components/layout/DashboardLayout';
import { employees, clientMessages, documents } from '@/data/mockData';

const AdminDashboard: React.FC = () => {
  const stats = [
    {
      label: 'Total Employés',
      value: employees.length,
      icon: Users,
      change: '+2 ce mois',
      color: 'bg-primary/10 text-primary',
    },
    {
      label: 'Messages en attente',
      value: clientMessages.filter(m => m.status === 'pending').length,
      icon: MessageSquare,
      change: '3 nouveaux',
      color: 'bg-warning/10 text-warning',
    },
    {
      label: 'Documents indexés',
      value: documents.length,
      icon: FileText,
      change: '+12 cette semaine',
      color: 'bg-success/10 text-success',
    },
    {
      label: 'Taux de réponse',
      value: '94%',
      icon: TrendingUp,
      change: '+5% vs dernier mois',
      color: 'bg-accent/10 text-accent',
    },
  ];

  return (
    <DashboardLayout>
      <div className="animate-fade-in">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-foreground mb-2">Tableau de bord Admin</h1>
          <p className="text-muted-foreground">Vue d'ensemble de la plateforme Smart Offer Finder</p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {stats.map((stat, index) => (
            <div
              key={stat.label}
              className="card-elevated p-6 animate-slide-up"
              style={{ animationDelay: `${index * 0.1}s` }}
            >
              <div className="flex items-start justify-between mb-4">
                <div className={`w-12 h-12 rounded-xl ${stat.color} flex items-center justify-center`}>
                  <stat.icon className="w-6 h-6" />
                </div>
              </div>
              <div className="text-3xl font-bold text-foreground mb-1">{stat.value}</div>
              <div className="text-sm text-muted-foreground mb-2">{stat.label}</div>
              <div className="text-xs text-success font-medium">{stat.change}</div>
            </div>
          ))}
        </div>

        {/* Recent Activity */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="card-elevated p-6">
            <h2 className="text-lg font-semibold text-foreground mb-4">Derniers Employés</h2>
            <div className="space-y-3">
              {employees.slice(0, 4).map((employee) => (
                <div key={employee.id} className="flex items-center gap-3 p-3 rounded-lg hover:bg-muted/50 transition-colors">
                  <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
                    <span className="text-sm font-semibold text-primary">
                      {employee.name.split(' ').map(n => n[0]).join('')}
                    </span>
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-medium text-foreground">{employee.name}</p>
                    <p className="text-xs text-muted-foreground">{employee.email}</p>
                  </div>
                  <span className={`text-xs px-2 py-1 rounded-full ${
                    employee.role === 'admin' 
                      ? 'bg-primary/10 text-primary' 
                      : 'bg-muted text-muted-foreground'
                  }`}>
                    {employee.role}
                  </span>
                </div>
              ))}
            </div>
          </div>

          <div className="card-elevated p-6">
            <h2 className="text-lg font-semibold text-foreground mb-4">Messages Récents</h2>
            <div className="space-y-3">
              {clientMessages.slice(0, 4).map((message) => (
                <div key={message.id} className="p-3 rounded-lg hover:bg-muted/50 transition-colors">
                  <div className="flex items-center justify-between mb-1">
                    <p className="text-sm font-medium text-foreground">{message.clientName}</p>
                    <span className={`text-xs px-2 py-1 rounded-full ${
                      message.status === 'pending' 
                        ? 'bg-warning/10 text-warning' 
                        : message.status === 'replied'
                        ? 'bg-success/10 text-success'
                        : 'bg-primary/10 text-primary'
                    }`}>
                      {message.status === 'pending' ? 'En attente' : 
                       message.status === 'replied' ? 'Répondu' : 'En cours'}
                    </span>
                  </div>
                  <p className="text-xs text-muted-foreground line-clamp-1">{message.subject}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
};

export default AdminDashboard;
