export const GITHUB_REPO_URL = 'https://github.com/afrodojo/hive-alignment';
export const LIVE_SITE_URL = 'https://hive-align.eds-360.com';

export const commitUrl = (hash) => `${GITHUB_REPO_URL}/commit/${hash}`;
export const fileUrl = (path) => `${GITHUB_REPO_URL}/blob/main/${path}`;
export const liveSiteHost = (url = LIVE_SITE_URL) =>
  url.replace(/^https?:\/\//, '').replace(/\/$/, '');