"""
Enhanced Developer Deduplication using Enhanced Bird Heuristic
"""

import csv
import unicodedata
import string
from itertools import combinations
from Levenshtein import ratio as sim
from collections import defaultdict


class EnhancedDeveloperDeduplication:
    """Enhanced Bird heuristic for developer deduplication"""

    def __init__(self, csv_path):
        self.csv_path = csv_path
        self.developers = []
        self.duplicates = []

    def load_developers(self):
        """Load developers from CSV file"""
        with open(self.csv_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            self.developers = [row for row in reader]
        print(f"Loaded {len(self.developers)} developers")

    def clean_name(self, name):
        """Clean and normalize name"""
        # Remove punctuation
        trans = name.maketrans("", "", string.punctuation)
        clean = name.translate(trans)

        # Unicode normalization (removes accents)
        clean = unicodedata.normalize('NFKD', clean)
        clean = ''.join([c for c in clean if not unicodedata.combining(c)])

        # Lowercase and normalize whitespace
        clean = clean.casefold()
        clean = " ".join(clean.split())

        return clean

    def process_developer(self, name, email):
        """Process developer information for comparison"""
        clean_name = self.clean_name(name)
        parts = clean_name.split()

        if len(parts) == 0:
            first, last = "", ""
        elif len(parts) == 1:
            first, last = parts[0], ""
        elif len(parts) == 2:
            first, last = parts
        else:
            first, last = parts[0], " ".join(parts[1:])

        # Extract initials
        i_first = first[0] if len(first) > 0 else ""
        i_last = last[0] if len(last) > 0 else ""

        # Process email
        email_lower = email.lower()
        prefix = email_lower.split("@")[0]
        domain = email_lower.split("@")[1] if "@" in email_lower else ""

        return {
            'clean_name': clean_name,
            'first': first,
            'last': last,
            'i_first': i_first,
            'i_last': i_last,
            'prefix': prefix,
            'domain': domain
        }

    def calculate_similarity(self, dev_a, dev_b):
        """Calculate enhanced Bird heuristic similarity"""
        # Original Bird conditions (C1-C7)
        c1 = sim(dev_a['clean_name'], dev_b['clean_name'])  # Full name similarity
        c2 = sim(dev_a['prefix'], dev_b['prefix'])           # Email prefix similarity
        c31 = sim(dev_a['first'], dev_b['first'])            # First name similarity
        c32 = sim(dev_a['last'], dev_b['last'])              # Last name similarity

        # Pattern matching conditions (C4-C7)
        c4 = c5 = c6 = c7 = False
        if dev_a['i_first'] and dev_a['last']:
            c4 = dev_a['i_first'] in dev_b['prefix'] and dev_a['last'] in dev_b['prefix']
        if dev_a['i_last']:
            c5 = dev_a['i_last'] in dev_b['prefix'] and dev_a['first'] in dev_b['prefix']
        if dev_b['i_first'] and dev_b['last']:
            c6 = dev_b['i_first'] in dev_a['prefix'] and dev_b['last'] in dev_a['prefix']
        if dev_b['i_last']:
            c7 = dev_b['i_last'] in dev_a['prefix'] and dev_b['first'] in dev_a['prefix']

        # Enhanced conditions (C8-C10)
        c8_domain_match = dev_a['domain'] == dev_b['domain']
        c9_institutional = dev_a['domain'] in ['microsoft.com', 'plainconcepts.com'] and c8_domain_match
        c10_prefix_substring = (dev_a['prefix'] in dev_b['prefix'] or
                               dev_b['prefix'] in dev_a['prefix']) and len(dev_a['prefix']) > 3

        # Weighted confidence score
        confidence = (
            c1 * 0.4 +                      # Name similarity (highest weight)
            c2 * 0.2 +                      # Email prefix similarity
            max(c31, c32) * 0.2 +           # Best name part similarity
            (c4 or c5 or c6 or c7) * 0.1 +  # Pattern matching
            c8_domain_match * 0.05 +        # Domain match
            c9_institutional * 0.05         # Institutional domain
        )

        return confidence

    def find_duplicates(self, threshold=0.6):
        """Find all duplicate pairs above confidence threshold"""
        print(f"\nAnalyzing developer pairs (threshold: {threshold})...")

        pair_count = 0
        for dev_a, dev_b in combinations(self.developers, 2):
            pair_count += 1

            if pair_count % 10000 == 0:
                print(f"  Analyzed {pair_count} pairs...")

            # Process both developers
            proc_a = self.process_developer(dev_a[0], dev_a[1])
            proc_b = self.process_developer(dev_b[0], dev_b[1])

            # Calculate confidence
            confidence = self.calculate_similarity(proc_a, proc_b)

            # Store if above threshold
            if confidence >= threshold:
                self.duplicates.append({
                    'name_1': dev_a[0],
                    'email_1': dev_a[1],
                    'name_2': dev_b[0],
                    'email_2': dev_b[1],
                    'confidence': confidence
                })

        # Sort by confidence (highest first)
        self.duplicates.sort(key=lambda x: x['confidence'], reverse=True)

        print(f"Analyzed {pair_count} total pairs")
        print(f"Found {len(self.duplicates)} duplicate pairs")

    def generate_clusters(self):
        """Group duplicate pairs into clusters"""
        clusters = defaultdict(set)
        cluster_id = 0

        for dup in self.duplicates:
            name1 = f"{dup['name_1']} <{dup['email_1']}>"
            name2 = f"{dup['name_2']} <{dup['email_2']}>"

            # Find existing clusters containing either name
            existing_clusters = []
            for cid, cluster in clusters.items():
                if name1 in cluster or name2 in cluster:
                    existing_clusters.append(cid)

            if not existing_clusters:
                # Create new cluster
                clusters[cluster_id] = {name1, name2}
                cluster_id += 1
            elif len(existing_clusters) == 1:
                # Add to existing cluster
                clusters[existing_clusters[0]].update({name1, name2})
            else:
                # Merge multiple clusters
                merged_cluster = {name1, name2}
                for cid in existing_clusters:
                    merged_cluster.update(clusters[cid])
                    del clusters[cid]
                clusters[cluster_id] = merged_cluster
                cluster_id += 1

        return dict(clusters)

    def save_results(self, output_dir="../results"):
        """Save results to files"""
        import os
        os.makedirs(output_dir, exist_ok=True)

        # Save duplicate pairs to CSV
        pairs_file = f"{output_dir}/duplicate_pairs.csv"
        with open(pairs_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['name_1', 'email_1', 'name_2', 'email_2', 'confidence'])
            for dup in self.duplicates:
                writer.writerow([
                    dup['name_1'], dup['email_1'],
                    dup['name_2'], dup['email_2'],
                    f"{dup['confidence']:.3f}"
                ])
        print(f"\nSaved duplicate pairs to: {pairs_file}")

        # Save clusters to text file
        clusters = self.generate_clusters()
        clusters_file = f"{output_dir}/duplicate_clusters.txt"
        with open(clusters_file, 'w', encoding='utf-8') as f:
            f.write("=" * 70 + "\n")
            f.write("DUPLICATE DEVELOPER CLUSTERS\n")
            f.write("=" * 70 + "\n\n")
            f.write(f"Total clusters found: {len(clusters)}\n\n")

            for cluster_id, cluster in clusters.items():
                f.write(f"Cluster {cluster_id + 1} ({len(cluster)} identities):\n")
                for identity in sorted(cluster):
                    f.write(f"  • {identity}\n")
                f.write("\n")

        print(f"Saved duplicate clusters to: {clusters_file}")

        # Print summary
        print(f"\n{'='*70}")
        print("SUMMARY")
        print(f"{'='*70}")
        print(f"Total developers:        {len(self.developers)}")
        print(f"Duplicate pairs found:   {len(self.duplicates)}")
        print(f"Duplicate clusters:      {len(clusters)}")
        print(f"{'='*70}")

        # Show top 10 duplicates
        if self.duplicates:
            print("\nTop 10 highest confidence duplicates:")
            for i, dup in enumerate(self.duplicates[:10], 1):
                print(f"{i:2d}. {dup['name_1']:30s} ↔ {dup['name_2']:30s} ({dup['confidence']:.3f})")


def main():
    """Main execution"""
    print("=" * 70)
    print("Enhanced Developer Deduplication - Enhanced Bird Heuristic")
    print("=" * 70)

    # Initialize
    analyzer = EnhancedDeveloperDeduplication("../data/ShopOnContainers/devs.csv")

    # Run analysis
    analyzer.load_developers()
    analyzer.find_duplicates(threshold=0.6)
    analyzer.save_results("../data/ShopOnContainers/results")

    print("\nDone!")


if __name__ == "__main__":
    main()
