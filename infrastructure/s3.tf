# Real-time Pageview Data Pipeline
# S3 Storage Configuration (LocalStack)

## S3 Buckets

# Raw pageview events storage (Optional: For data lake or debug)
resource "aws_s3_bucket" "raw_events" {
  bucket = "${var.project_name}-${terraform.workspace}-raw-events"

  tags = merge(local.common_tags, {
    Purpose = "Raw pageview events storage"
  })
}

resource "aws_s3_bucket_lifecycle_configuration" "raw_events" {
  bucket = aws_s3_bucket.raw_events.id

  rule {
    id     = "expire-raw-events"
    status = "Enabled"

    transition {
      days          = 30
      storage_class = "GLACIER"
    }

    # Option of removing after 90 days
    # expiration {
    #   days = 90
    # }
  }
}



# Aggregated results storage (Flink Sink)
resource "aws_s3_bucket" "aggregated" {
  bucket = "${var.project_name}-${terraform.workspace}-aggregated"

  tags = merge(local.common_tags, {
    Purpose = "Aggregated pageview results"
  })
}

resource "aws_s3_bucket_lifecycle_configuration" "aggregated" {
  bucket = aws_s3_bucket.aggregated.id

  rule {
    id     = "expire-aggregated-results"
    status = "Enabled"

    transition {
      days          = 30
      storage_class = "GLACIER"
    }

    # Option of removing after 90 days
    # expiration {
    #   days = 90
    # }
  }
}

# Dead Letter Queue storage (For malformed events)
resource "aws_s3_bucket" "dlq" {
  bucket = "${var.project_name}-${terraform.workspace}-dlq"

  tags = merge(local.common_tags, {
    Purpose = "Malformed event storage (DLQ)"
  })
}

resource "aws_s3_bucket_lifecycle_configuration" "dlq" {
  bucket = aws_s3_bucket.dlq.id

  rule {
    id     = "expire-dlq-events"
    status = "Enabled"

    transition {
      days          = 30
      storage_class = "GLACIER"
    }

    # Auto-expire after 90 days as DLQ items are usually time-sensitive
    expiration {
      days = 90
    }
  }
}



## IAM Policies for Data Access

# Policy for reading/writing S3 data buckets
data "aws_iam_policy_document" "s3_data_access" {
  statement {
    actions = [
      "s3:GetObject",
      "s3:PutObject",
      "s3:DeleteObject"
    ]
    resources = [
      "${aws_s3_bucket.raw_events.arn}/*",
      "${aws_s3_bucket.aggregated.arn}/*",
      "${aws_s3_bucket.dlq.arn}/*"
    ]
  }

  statement {
    actions = [
      "s3:ListBucket"
    ]
    resources = [
      aws_s3_bucket.raw_events.arn,
      aws_s3_bucket.aggregated.arn,
      aws_s3_bucket.dlq.arn
    ]
  }
}

resource "aws_iam_policy" "s3_data_access" {
  name   = "${var.project_name}-${terraform.workspace}-s3-data-access"
  policy = data.aws_iam_policy_document.s3_data_access.json

  tags = local.common_tags
}
