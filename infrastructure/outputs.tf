# S3 Bucket Outputs
output "raw_events_bucket" {
  description = "S3 bucket for raw pageview events"
  value       = aws_s3_bucket.raw_events.bucket
}

output "aggregated_bucket" {
  description = "S3 bucket for aggregated results"
  value       = aws_s3_bucket.aggregated.bucket
}

output "s3_access_policy_arn" {
  description = "ARN of the IAM policy for S3 access"
  value       = aws_iam_policy.s3_data_access.arn
}
