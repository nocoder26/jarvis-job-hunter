import JobCard from './JobCard'

type Job = {
  id: string
  title: string
  description: string | null
  location: string | null
  status: string
  discovered_at: string
  application_url: string | null
  companies: {
    id: string
    name: string
    is_enisa_certified: boolean
    is_startup_law: boolean
  } | null
  job_analysis: {
    fit_score: number
    spanish_required: boolean
    visa_status: string
    fit_summary: string
    skills_matched: string[]
    skills_missing: string[]
  } | null
}

export default function JobList({
  jobs,
  onRefresh
}: {
  jobs: Job[]
  onRefresh: () => void
}) {
  // Sort by fit score (highest first), then by discovered date
  const sortedJobs = [...jobs].sort((a, b) => {
    const scoreA = a.job_analysis?.fit_score ?? -1
    const scoreB = b.job_analysis?.fit_score ?? -1

    if (scoreA !== scoreB) {
      return scoreB - scoreA
    }

    return new Date(b.discovered_at).getTime() - new Date(a.discovered_at).getTime()
  })

  return (
    <div className="space-y-4">
      {sortedJobs.map((job) => (
        <JobCard key={job.id} job={job} onRefresh={onRefresh} />
      ))}
    </div>
  )
}
