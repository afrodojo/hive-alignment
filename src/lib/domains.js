import { Compass, Crown, Cpu, ShieldCheck, Users, TrendingUp } from 'lucide-react';

export const DOMAIN_ORDER = [
  'SPIRITUAL_PILLARS',
  'CYBER_DEFENSE',
  'OMEGA_HISTORY',
  'CS_RESEARCH',
  'COMMUNITY_UPLIFT',
  'BIZ_ACUMEN',
];

export const DOMAINS = {
  SPIRITUAL_PILLARS: {
    label: 'Spiritual Pillars',
    shortLabel: 'Spiritual',
    focus: 'Ihsan · Amanah · Niyyah',
    icon: Compass,
    badge: 'text-emerald-400 bg-emerald-950/40 border-emerald-500/40',
    dot: 'bg-emerald-400',
    rule: 'border-emerald-500/40',
    line: 'from-emerald-400/70 via-emerald-400/20',
    bar: 'bg-emerald-400',
    text: 'text-emerald-400',
  },
  CYBER_DEFENSE: {
    label: 'Cyber Defense',
    shortLabel: 'Cyber',
    focus: 'Zero-trust · Adversary · Assurance',
    icon: ShieldCheck,
    badge: 'text-rose-400 bg-rose-950/40 border-rose-500/40',
    dot: 'bg-rose-400',
    rule: 'border-rose-500/40',
    line: 'from-rose-400/70 via-rose-400/20',
    bar: 'bg-rose-400',
    text: 'text-rose-400',
  },
  OMEGA_HISTORY: {
    label: 'Omega History',
    shortLabel: 'Omega',
    focus: 'Manhood · Scholarship · Perseverance · Uplift',
    icon: Crown,
    badge: 'text-amber-400 bg-purple-950/40 border-amber-500/40',
    dot: 'bg-amber-400',
    rule: 'border-amber-500/40',
    line: 'from-amber-400/70 via-purple-400/20',
    bar: 'bg-amber-400',
    text: 'text-amber-400',
  },
  CS_RESEARCH: {
    label: 'CS Research',
    shortLabel: 'Research',
    focus: 'Consensus · Invariants · Entropy',
    icon: Cpu,
    badge: 'text-cyan-400 bg-cyan-950/40 border-cyan-500/40',
    dot: 'bg-cyan-400',
    rule: 'border-cyan-500/40',
    line: 'from-cyan-400/70 via-cyan-400/20',
    bar: 'bg-cyan-400',
    text: 'text-cyan-400',
  },
  COMMUNITY_UPLIFT: {
    label: 'Community Uplift',
    shortLabel: 'Uplift',
    focus: 'Talent pipelines · Equity · Access',
    icon: Users,
    badge: 'text-orange-400 bg-orange-950/40 border-orange-500/40',
    dot: 'bg-orange-400',
    rule: 'border-orange-500/40',
    line: 'from-orange-400/70 via-orange-400/20',
    bar: 'bg-orange-400',
    text: 'text-orange-400',
  },
  BIZ_ACUMEN: {
    label: 'Biz Acumen',
    shortLabel: 'Acumen',
    focus: 'GovCon · Margins · Leadership',
    icon: TrendingUp,
    badge: 'text-blue-400 bg-blue-950/40 border-blue-500/40',
    dot: 'bg-blue-400',
    rule: 'border-blue-500/40',
    line: 'from-blue-400/70 via-blue-400/20',
    bar: 'bg-blue-400',
    text: 'text-blue-400',
  },
};

export function domainMeta(key) {
  return DOMAINS[key] || DOMAINS.SPIRITUAL_PILLARS;
}