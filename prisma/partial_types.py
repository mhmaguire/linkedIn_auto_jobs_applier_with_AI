from prisma.models import Job


Job.create_partial(
    "JobWithCompany",
    include={
        "id",
        "company",
        "external_id",
        "title",
        "link",
        "description",
        "summary",
        "apply_method",
        "created_at",
        "updated_at",
    },
)
