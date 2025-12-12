import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sparkles, Mail, Lock, ArrowRight } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useAuth } from '@/contexts/AuthContext';
import { toast } from '@/hooks/use-toast';

const Login: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 800));

    const success = login(email, password);
    
    if (success) {
      toast({
        title: 'Connexion réussie',
        description: 'Bienvenue sur Smart Offer Finder',
      });
      // Redirect based on role
      if (email.includes('admin') || email === 'ahmed.bensalem@company.tn') {
        navigate('/admin');
      } else {
        navigate('/employee');
      }
    } else {
      toast({
        title: 'Erreur de connexion',
        description: 'Email ou mot de passe incorrect',
        variant: 'destructive',
      });
    }
    
    setIsLoading(false);
  };

  const demoAccounts = [
    { email: 'ahmed.bensalem@company.tn', role: 'Admin' },
    { email: 'fatma.trabelsi@company.tn', role: 'Employee' },
  ];

  return (
    <div className="min-h-screen bg-background flex">
      {/* Left Panel - Branding */}
      <div className="hidden lg:flex lg:w-1/2 bg-primary relative overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_30%_50%,hsl(217_91%_70%/0.3),transparent_50%)]"></div>
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_70%_80%,hsl(217_91%_40%/0.4),transparent_50%)]"></div>
        
        <div className="relative z-10 flex flex-col justify-center px-12 text-primary-foreground">
          <div className="flex items-center gap-3 mb-8">
            <div className="w-12 h-12 rounded-xl bg-primary-foreground/20 flex items-center justify-center backdrop-blur-sm">
              <Sparkles className="w-7 h-7" />
            </div>
            <span className="text-2xl font-bold">Smart Offer Finder</span>
          </div>
          
          <h1 className="text-4xl font-bold mb-4 leading-tight">
            Assistant IA pour<br />Agents Front Office
          </h1>
          <p className="text-lg text-primary-foreground/80 max-w-md">
            Optimisez vos réponses clients grâce à l'intelligence artificielle et la recherche documentaire intelligente.
          </p>

          <div className="mt-12 grid grid-cols-2 gap-6">
            <div className="bg-primary-foreground/10 backdrop-blur-sm rounded-xl p-4">
              <div className="text-3xl font-bold mb-1">95%</div>
              <div className="text-sm text-primary-foreground/70">Temps de réponse réduit</div>
            </div>
            <div className="bg-primary-foreground/10 backdrop-blur-sm rounded-xl p-4">
              <div className="text-3xl font-bold mb-1">500+</div>
              <div className="text-sm text-primary-foreground/70">Documents indexés</div>
            </div>
          </div>
        </div>
      </div>

      {/* Right Panel - Login Form */}
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="w-full max-w-md animate-fade-in">
          <div className="lg:hidden flex items-center gap-3 mb-8 justify-center">
            <div className="w-10 h-10 rounded-lg bg-primary flex items-center justify-center">
              <Sparkles className="w-6 h-6 text-primary-foreground" />
            </div>
            <span className="text-xl font-bold text-foreground">Smart Offer Finder</span>
          </div>

          <div className="card-elevated p-8">
            <div className="mb-8">
              <h2 className="text-2xl font-bold text-foreground mb-2">Connexion</h2>
              <p className="text-muted-foreground">Entrez vos identifiants pour accéder à la plateforme</p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-5">
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
                  <Input
                    id="email"
                    type="email"
                    placeholder="votre.email@company.tn"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="pl-10 h-11"
                    required
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="password">Mot de passe</Label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
                  <Input
                    id="password"
                    type="password"
                    placeholder="••••••••"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="pl-10 h-11"
                    required
                  />
                </div>
              </div>

              <Button type="submit" className="w-full h-11" disabled={isLoading}>
                {isLoading ? (
                  <span className="flex items-center gap-2">
                    <span className="w-4 h-4 border-2 border-primary-foreground/30 border-t-primary-foreground rounded-full animate-spin"></span>
                    Connexion...
                  </span>
                ) : (
                  <span className="flex items-center gap-2">
                    Se connecter
                    <ArrowRight className="w-4 h-4" />
                  </span>
                )}
              </Button>
            </form>

            {/* Demo Accounts */}
            <div className="mt-8 pt-6 border-t border-border">
              <p className="text-sm text-muted-foreground mb-3">Comptes de démonstration :</p>
              <div className="space-y-2">
                {demoAccounts.map((account) => (
                  <button
                    key={account.email}
                    onClick={() => {
                      setEmail(account.email);
                      setPassword('demo123');
                    }}
                    className="w-full text-left px-3 py-2 rounded-lg bg-muted hover:bg-muted/80 transition-colors text-sm"
                  >
                    <span className="font-medium text-foreground">{account.role}</span>
                    <span className="text-muted-foreground ml-2">{account.email}</span>
                  </button>
                ))}
              </div>
              <p className="text-xs text-muted-foreground mt-3">Mot de passe : demo123</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
