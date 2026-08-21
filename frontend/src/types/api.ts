export interface CrawlTaskStatus {
  task_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  pages_crawled: number;
  pages_failed: number;
  duration_seconds: number;
}

export interface CrawlStats {
  pages_crawled: number;
  pages_failed: number;
  duration_seconds: number;
}

export interface SEOIssue {
  rule_id: string;
  severity: 'error' | 'warning' | 'info';
  message: string;
  element?: string | null;
}

export interface PageReport {
  url: string;
  status_code?: number | null;
  title?: string | null;
  meta_description?: string | null;
  canonical_url?: string | null;
  language?: string | null;
  robots_meta?: string | null;
  h1_tags: string[];
  h2_tags: string[];
  h3_tags: string[];
  internal_links: string[];
  seo_issues: SEOIssue[];
}

export interface HealthIssue {
  url: string;
  issue_type: string;
  description: string;
}

export interface CrawlReport {
  start_url: string;
  stats: CrawlStats;
  pages: PageReport[];
  health_issues: HealthIssue[];
}
