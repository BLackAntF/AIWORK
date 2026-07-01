type LogLevel = 'debug' | 'info' | 'warn' | 'error' | 'silent';

const LOG_LEVELS: Record<LogLevel, number> = {
  debug: 0,
  info: 1,
  warn: 2,
  error: 3,
  silent: 4,
};

const getLogLevel = (): LogLevel => {
  const envLevel = import.meta.env.VITE_LOG_LEVEL;
  if (envLevel && Object.keys(LOG_LEVELS).includes(envLevel)) {
    return envLevel as LogLevel;
  }
  return import.meta.env.PROD ? 'error' : 'debug';
};

const currentLevel = getLogLevel();

const shouldLog = (level: LogLevel): boolean => {
  return LOG_LEVELS[level] >= LOG_LEVELS[currentLevel];
};

export const logger = {
  debug: (...args: unknown[]): void => {
    if (shouldLog('debug')) {
      console.debug('[DEBUG]', ...args);
    }
  },
  info: (...args: unknown[]): void => {
    if (shouldLog('info')) {
      console.info('[INFO]', ...args);
    }
  },
  warn: (...args: unknown[]): void => {
    if (shouldLog('warn')) {
      console.warn('[WARN]', ...args);
    }
  },
  error: (...args: unknown[]): void => {
    if (shouldLog('error')) {
      console.error('[ERROR]', ...args);
    }
  },
};
