import { EmptyState } from './EmptyState';
import { PageContainer } from './PageContainer';
import { SectionCard } from './SectionCard';

interface PlaceholderPageProps {
  title: string;
  subtitle: string;
}

export function PlaceholderPage({ title, subtitle }: PlaceholderPageProps) {
  return (
    <PageContainer title={title} subtitle={subtitle}>
      <SectionCard>
        <EmptyState
          title="Ready for the next slice"
          message="This route is intentionally present to establish navigation and layout without building bookkeeping workflows in Phase 1C."
        />
      </SectionCard>
    </PageContainer>
  );
}
