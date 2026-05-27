
export enum ConnectionStatus {
  CONNECTED = 'connected',
  DISCONNECTED = 'disconnected',
  CONNECTING = 'connecting'
}

export interface CommandEntry {
  id: string;
  command: string;
  response: string;
  timestamp: Date;
  status: 'success' | 'error' | 'pending';
}

export interface SystemMetrics {
  cpu: number;
  ram: number;
  disk: number;
  uptime: string;
}

export interface JarvisConfig {
  backendUrl: string;
  wsUrl: string;
  apiKey: string;
  theme: 'dark' | 'light';
  autoConnect: boolean;
}

export interface AppState {
  status: ConnectionStatus;
  metrics: SystemMetrics;
  history: CommandEntry[];
  config: JarvisConfig;
}
