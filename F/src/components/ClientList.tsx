import { Client } from '@/types';
import { cn } from '@/lib/utils';
import { formatDistanceToNow } from 'date-fns';
import { User } from 'lucide-react';

interface ClientListProps {
  clients: Client[];
  selectedClientId: string | null;
  onSelectClient: (client: Client) => void;
}

export function ClientList({ clients, selectedClientId, onSelectClient }: ClientListProps) {
  return (
    <div className="flex flex-col h-full bg-sidebar">
      <div className="p-4 border-b border-sidebar-border">
        <h2 className="text-lg font-semibold text-sidebar-foreground">Client Messages</h2>
        <p className="text-sm text-muted-foreground mt-1">{clients.length} conversations</p>
      </div>
      
      <div className="flex-1 overflow-y-auto">
        {clients.map((client) => (
          <button
            key={client.id}
            onClick={() => onSelectClient(client)}
            className={cn(
              "w-full p-4 text-left border-b border-sidebar-border transition-all duration-200",
              "hover:bg-sidebar-accent focus:outline-none focus:bg-sidebar-accent",
              "active:scale-[0.99]",
              selectedClientId === client.id && "bg-sidebar-accent border-l-4 border-l-primary"
            )}
          >
            <div className="flex items-start gap-3">
              <div className={cn(
                "w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0",
                "bg-primary/10 text-primary"
              )}>
                <User className="w-5 h-5" />
              </div>
              
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between gap-2">
                  <span className={cn(
                    "font-medium truncate",
                    client.unread ? "text-sidebar-foreground" : "text-muted-foreground"
                  )}>
                    {client.name}
                  </span>
                  <span className="text-xs text-muted-foreground flex-shrink-0">
                    {formatDistanceToNow(client.lastMessageTime, { addSuffix: true })}
                  </span>
                </div>
                
                <p className={cn(
                  "text-sm mt-1 line-clamp-2",
                  client.unread ? "text-sidebar-foreground" : "text-muted-foreground"
                )}>
                  {client.lastMessage}
                </p>
                
                {client.unread && (
                  <span className="inline-block w-2 h-2 rounded-full bg-primary mt-2" />
                )}
              </div>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
