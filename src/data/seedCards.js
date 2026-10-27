/**
 * Static seed insights for the non-research domains. These ship with the client
 * bundle so the feed renders instantly and never depends on a database read.
 */
export const SEED_CARDS = [
  {
    id: '6ae0e571eb6ee78fa281c9df',
    domain: 'SPIRITUAL_PILLARS',
    title: 'Niyyah Is the Compiler',
    hook: 'Every act is judged by its intention — one program, two very different outputs.',
    core_insight:
      'Intention is the semantic layer of action. The same transaction, the same code review, the same payroll run compiles into either worship or noise depending on the niyyah behind it. The Prophet ﷺ defined ihsan as worshipping "as though you see Him" — a standard of visibility, not of volume. In enterprise terms: ihsan is defect-free craft performed under audit; amanah is authority bounded by trust, so nobody holds a key they are not liable to answer for. Adab is the interface contract that keeps all three legible to other people.',
    takeaways: [
      'Name the intention before the action — a one-line niyyah note on the ticket.',
      'Calibrate authority to liability: if you cannot answer for it, you do not sign it.',
      'Treat excellence as a floor, not an aspiration: the standard is the One who sees.',
    ],
    proof_or_code:
      'niyyah : intent ⊳ outcome        // intent governs the reward, not the scale\nihsan  : quality(act) = max     // no defect hidden under deadline\namanah : authority ≤ trust      // a key is a liability, not a perk\nadab   : interface(honest, clear, unhurried)',
    read_time_seconds: 50,
    repo_url: 'https://github.com/afrodojo/hive-alignment',
    live_site_url: 'https://hive-align.eds-360.com',
  },
  {
    id: '6ae0e571eb6ee78fa281c9e0',
    domain: 'OMEGA_HISTORY',
    title: 'Ernest E. Just: Scholarship as Perseverance',
    hook: 'He mapped the cell surface before biology had a name for it — without a single lab of his own.',
    core_insight:
      "On 17 November 1911, three Howard undergraduates — Edgar Amos Love, Oscar James Cooper, and Frank Coleman — founded Omega Psi Phi with their faculty adviser, Dr. Ernest Everett Just. Just's own science was the cardinal principles made method: he studied fertilization and the ectoplasm at the Marine Biological Laboratory at Woods Hole, then in Naples, Berlin, and Paris, because American institutions would not fund a Black principal investigator. Perseverance was not a slogan for him; it was the experimental design. He received the first Spingarn Medal in 1915 and published The Biology of the Cell Surface in 1939 — a thesis on the active role of the cell membrane that the field would only vindicate decades later.",
    takeaways: [
      'Perseverance is a research method: hold the question fixed and change the venue.',
      'Scholarship is self-defense; a citation is a weapon that outlives the gatekeeper.',
      'Uplift is structural — found the institution that will fund the next person.',
    ],
    proof_or_code:
      '1911.11.17  Omega Psi Phi founded @ Howard University\n1915        Just awarded the first Spingarn Medal\n1939        The Biology of the Cell Surface published\n2026        Manhood · Scholarship · Perseverance · Uplift',
    read_time_seconds: 55,
    repo_url: 'https://github.com/afrodojo/hive-alignment',
    live_site_url: 'https://hive-align.eds-360.com',
  },
  {
    id: '6ae0e571eb6ee78fa281c9e5',
    domain: 'SPIRITUAL_PILLARS',
    title: 'Amanah: The Liability of the Key',
    hook: 'Every privilege you hold is a trust you will be asked about.',
    core_insight:
      'Amanah reframes access control as moral accounting. The database credential, the production deploy, the salary spreadsheet — each is a trust with an attached liability, and the classical scholars treated misuse of a trust as betrayal rather than a policy violation. That maps cleanly onto least privilege: authority should never exceed accountability. Gharar, the prohibition of excessive uncertainty in contracts, is the same instinct applied to commerce — do not sell what you cannot describe. Ihsan then supplies the standard: the work is done as if seen, which means the audit trail is honest even when nobody is reading it.',
    takeaways: [
      'Grant the narrowest key that completes the task, and log who held it.',
      'Say the uncertainty out loud in the contract; ambiguity is a liability, not leverage.',
      'Write the audit trail for the One who sees, not for the reviewer who might.',
    ],
    proof_or_code: 'amanah  ⇒ authority ≤ accountability\ngharar  ⇒ ¬contract(undefined_terms)\nihsan   ⇒ audit_honest even when unobserved',
    read_time_seconds: 45,
    repo_url: 'https://github.com/afrodojo/hive-alignment',
    live_site_url: 'https://hive-align.eds-360.com',
  },
  {
    id: '6ae0e571eb6ee78fa281c9e2',
    domain: 'COMMUNITY_UPLIFT',
    title: 'A Pipeline That Leaks Is a Drain',
    hook: "If the talent, the clearance, and the capital all leave, you built a training program for someone else's economy.",
    core_insight:
      'Sovereign talent pipelines are an economics problem disguised as a representation problem. A program that produces cleared cyber operators but exports every graduate has negative local return: the community absorbs the training cost and the coastal contractor captures the wage premium. The fix is structural — earn-while-learn apprenticeships tied to local employers, HBCU labs wired into the defense industrial base, and ownership stakes (subcontracts, SBIR vehicles, joint ventures) so the margin stays where the capability was grown. Mentor the person and the balance sheet.',
    takeaways: [
      'Fund apprenticeships with a retention clause, not a scholarship with a goodbye.',
      'Route graduates into anchored primes, subcontracts, or a shared services co-op.',
      'Track the metric that matters: cleared talent still employed locally after 24 months.',
    ],
    proof_or_code:
      "sovereign_return = placements × retention_local × wage_premium_retained\nleak             = graduates − retained_after_24mo\n\nif leak > 0: the community subsidized someone else's margin",
    read_time_seconds: 50,
    repo_url: 'https://github.com/afrodojo/hive-alignment',
    live_site_url: 'https://hive-align.eds-360.com',
  },
  {
    id: '6ae0e571eb6ee78fa281c9e3',
    domain: 'BIZ_ACUMEN',
    title: 'Your Margin Is a Derivative of Inference Prices',
    hook: 'You did not sign up to trade compute futures — but your gross margin now does it for you.',
    core_insight:
      'In GovCon the wrap rate is the whole story: (direct + indirect + G&A) ÷ direct. Under FFP every point of unhedged inference cost lands directly on fee. Under cost-plus it lands on your provisional billing rate and your next audit. So model inference as a commodity input with variance, not as a subscription: reserve baseline throughput, route burst to on-demand, cache aggressively, and distill the 80% of calls that never needed a frontier model. Then check the compliance surface — CMMC Level 2 against NIST SP 800-171, DISA STIGs on the enclave — because a failed assessment costs more than a year of GPU spend.',
    takeaways: [
      'Quote FFP with a variance buffer sized to p95 inference cost, never the median.',
      'Distill and cache before you renegotiate: most tokens are spent on solved problems.',
      'Budget CMMC and STIG conformance as quarterly unit cost, not a one-time sprint.',
    ],
    proof_or_code:
      'wrap_rate    = (direct + indirect + G&A) / direct\ngross_margin = (price − direct − inference_cost) / price\nhedge        : reserve ≥ p50 demand, burst ≤ p95 − p50, cache_hit ≥ 0.4',
    read_time_seconds: 55,
    repo_url: 'https://github.com/afrodojo/hive-alignment',
    live_site_url: 'https://hive-align.eds-360.com',
  },
];