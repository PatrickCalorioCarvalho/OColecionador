import { Play, StopCircle, RefreshCw } from 'lucide-react';import { Container } from '../models/Docker';
import './ContainerCard.css';

interface Props {
  containers: Container[];
  onAction: (action: string, id: string) => void;
}

export function ContainerCard({ containers, onAction }: Props) {
  const getRowClass = (state: string) => {
    switch (state) {
      case 'running':
        return 'row-running';
      case 'exited':
        return 'row-exited';
      case 'created':
        return 'row-created';
      default:
        return '';
    }
  };

  return (
    <div className="table-card">
      <h2>Containers Docker</h2>
      <table>
        <thead>
          <tr>
            <th>Nome</th>
            <th>Status</th>
            <th>Ações</th>
          </tr>
        </thead>
        <tbody>
          {containers.map((c) => (
            <tr key={c.id} className={getRowClass(c.status)}>
              <td>{c.names?.[0]?.replace('/', '') || 'Sem nome'}</td>
              <td>{c.status}</td>
              <td>
                {c.status !== 'running' && (
                  <button onClick={() => onAction('start',c.id)} title="Iniciar">
                    <Play size={18} />
                  </button>
                )}
                {c.status === 'running' && (
                  <button onClick={() => onAction('stop', c.id)} title="Parar">
                    <StopCircle size={18} />
                  </button>
                )}
                <button onClick={() => onAction('restart', c.id)} title="Reiniciar">
                  <RefreshCw size={18} />
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}