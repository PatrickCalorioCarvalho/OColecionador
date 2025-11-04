
import { Container } from '../models/Docker';
import { Play, StopCircle, RefreshCw } from 'lucide-react';
import './ContainerCard.css';

interface Props {
  container: Container;
  onAction: (action: string, id: string) => void;
}

export function ContainerCard({ container, onAction }: Props) {

  type ContainerState = 'running' | 'exited' | 'created';

  const statusColor: Record<ContainerState, string> = {
    running: '#4caf50',
    exited: '#f44336',
    created: '#ff9800',
  };

  const color = statusColor[container.status as ContainerState] ?? '#000';

  return (
    <div className="container-card">
      <h3>{container.names?.[0]?.replace('/', '') || 'Sem nome'}</h3>
      <p><strong>Imagem:</strong> {container.image}</p>
      <p><strong>Comando:</strong> {container.command}</p>
      <p>


        <strong>Status:</strong>{' '}
        <span style={{ color, fontWeight: 'bold' }}>{container.state}</span>
      </p>
      <div className="actions">
        {container.state !== 'running' && (
          <button onClick={() => onAction('start', container.id)} title="Iniciar">
            <Play />
          </button>
        )}
        {container.state === 'running' && (
          <button onClick={() => onAction('stop', container.id)} title="Parar">
            <StopCircle />
          </button>
        )}
        <button onClick={() => onAction('restart', container.id)} title="Reiniciar">
          <RefreshCw />
        </button>
      </div>
    </div>
  );
}
