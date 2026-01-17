from typing import List, Optional
from datetime import datetime
import resend

from src.utils.config import get_settings

settings = get_settings()


class EmailService:
    """Service for sending emails via Resend."""

    SUPPORT_EMAIL = "support@federalfraudwatch.com"
    SITE_URL = "https://federalfraudwatch.com"

    def __init__(self):
        self.api_key = settings.resend_api_key
        self.from_email = settings.from_email
        if self.api_key:
            resend.api_key = self.api_key

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        plain_content: Optional[str] = None,
        reply_to: Optional[str] = None,
    ) -> bool:
        """Send a single email."""
        if not self.api_key:
            print(f"Email service not configured. Would send to: {to_email}")
            return False

        try:
            params = {
                "from": f"Federal Fraud Watch <{self.from_email}>",
                "to": [to_email],
                "subject": subject,
                "html": html_content,
            }
            if plain_content:
                params["text"] = plain_content
            if reply_to:
                params["reply_to"] = reply_to

            resend.Emails.send(params)
            return True
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False

    async def send_bulk_email(
        self,
        recipients: List[str],
        subject: str,
        html_content: str,
        plain_content: Optional[str] = None,
    ) -> dict:
        """Send bulk emails using Resend batch API."""
        if not self.api_key:
            print(f"Email service not configured. Would send to {len(recipients)} recipients")
            return {"sent": 0, "failed": len(recipients)}

        # Resend batch API supports up to 100 emails per request
        batch_size = 100
        sent = 0
        failed = 0

        for i in range(0, len(recipients), batch_size):
            batch = recipients[i:i + batch_size]

            emails = []
            for email in batch:
                params = {
                    "from": f"Federal Fraud Watch <{self.from_email}>",
                    "to": [email],
                    "subject": subject,
                    "html": html_content,
                }
                if plain_content:
                    params["text"] = plain_content
                emails.append(params)

            try:
                resend.Batch.send(emails)
                sent += len(batch)
            except Exception as e:
                print(f"Batch email failed: {e}")
                failed += len(batch)

        return {"sent": sent, "failed": failed}

    # ==================== AUTOMATED EMAIL METHODS ====================

    async def send_welcome_email(self, to_email: str, name: Optional[str], tier: str) -> bool:
        """Send welcome email when user signs up."""
        subject = "Welcome to Federal Fraud Watch"
        html = self._generate_welcome_html(name, tier)
        return await self.send_email(to_email, subject, html)

    async def send_subscription_confirmation(self, to_email: str, name: Optional[str], tier: str, amount: int) -> bool:
        """Send confirmation when subscription is purchased."""
        subject = f"Your {tier.title()} Subscription is Active"
        html = self._generate_subscription_confirmation_html(name, tier, amount)
        return await self.send_email(to_email, subject, html)

    async def send_subscription_upgraded(self, to_email: str, name: Optional[str], old_tier: str, new_tier: str) -> bool:
        """Send notification when subscription is upgraded."""
        subject = f"You've Upgraded to {new_tier.title()}!"
        html = self._generate_upgrade_html(name, old_tier, new_tier)
        return await self.send_email(to_email, subject, html)

    async def send_subscription_downgraded(self, to_email: str, name: Optional[str], old_tier: str, new_tier: str) -> bool:
        """Send notification when subscription is downgraded."""
        subject = "Your Subscription Has Been Updated"
        html = self._generate_downgrade_html(name, old_tier, new_tier)
        return await self.send_email(to_email, subject, html)

    async def send_subscription_canceled(self, to_email: str, name: Optional[str], tier: str, end_date: datetime) -> bool:
        """Send notification when subscription is canceled."""
        subject = "We're Sorry to See You Go"
        html = self._generate_cancellation_html(name, tier, end_date)
        return await self.send_email(to_email, subject, html)

    async def send_payment_failed(self, to_email: str, name: Optional[str], tier: str) -> bool:
        """Send notification when payment fails."""
        subject = "Action Required: Payment Failed"
        html = self._generate_payment_failed_html(name, tier)
        return await self.send_email(to_email, subject, html)

    async def send_payment_receipt(self, to_email: str, name: Optional[str], tier: str, amount: int, invoice_id: str) -> bool:
        """Send payment receipt."""
        subject = f"Payment Receipt - Federal Fraud Watch"
        html = self._generate_receipt_html(name, tier, amount, invoice_id)
        return await self.send_email(to_email, subject, html)

    async def send_support_confirmation(self, to_email: str, name: Optional[str], ticket_id: str, subject_line: str) -> bool:
        """Send confirmation when support ticket is created."""
        subject = f"Support Request Received [#{ticket_id}]"
        html = self._generate_support_confirmation_html(name, ticket_id, subject_line)
        return await self.send_email(to_email, subject, html, reply_to=self.SUPPORT_EMAIL)

    async def send_support_reply(self, to_email: str, name: Optional[str], ticket_id: str, reply_content: str) -> bool:
        """Send support reply to user."""
        subject = f"Re: Support Request [#{ticket_id}]"
        html = self._generate_support_reply_html(name, ticket_id, reply_content)
        return await self.send_email(to_email, subject, html, reply_to=self.SUPPORT_EMAIL)

    async def send_password_reset(self, to_email: str, name: Optional[str], reset_link: str) -> bool:
        """Send password reset email."""
        subject = "Reset Your Password"
        html = self._generate_password_reset_html(name, reset_link)
        return await self.send_email(to_email, subject, html)

    async def send_email_verification(self, to_email: str, name: Optional[str], verification_link: str) -> bool:
        """Send email verification link."""
        subject = "Verify Your Email Address"
        html = self._generate_email_verification_html(name, verification_link)
        return await self.send_email(to_email, subject, html)

    async def send_new_article_notification(self, to_email: str, name: Optional[str], article_title: str, article_excerpt: str, article_url: str) -> bool:
        """Send notification for new article."""
        subject = f"New Article: {article_title}"
        html = self._generate_new_article_html(name, article_title, article_excerpt, article_url)
        return await self.send_email(to_email, subject, html)

    async def send_trial_ending_reminder(self, to_email: str, name: Optional[str], days_left: int) -> bool:
        """Send reminder before trial ends."""
        subject = f"Your Trial Ends in {days_left} Day{'s' if days_left != 1 else ''}"
        html = self._generate_trial_ending_html(name, days_left)
        return await self.send_email(to_email, subject, html)

    async def notify_admin_new_signup(self, user_email: str, tier: str) -> bool:
        """Notify admin of new signup."""
        subject = f"New Signup: {tier.title()} - {user_email}"
        html = f"<p>New user signed up:</p><p>Email: {user_email}<br>Tier: {tier}</p>"
        return await self.send_email(self.SUPPORT_EMAIL, subject, html)

    async def notify_admin_support_request(self, user_email: str, ticket_id: str, subject_line: str, message: str) -> bool:
        """Notify admin of new support request."""
        subject = f"New Support Request [#{ticket_id}]: {subject_line}"
        html = f"<p>From: {user_email}</p><p>Subject: {subject_line}</p><p>Message:</p><p>{message}</p>"
        return await self.send_email(self.SUPPORT_EMAIL, subject, html, reply_to=user_email)

    # ==================== HTML TEMPLATE GENERATORS ====================

    def _base_template(self, content: str) -> str:
        """Base HTML template wrapper."""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: Georgia, 'Times New Roman', serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f9f9f9;
                }}
                .header {{
                    background-color: #1a365d;
                    color: white;
                    padding: 20px;
                    text-align: center;
                    margin-bottom: 20px;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 24px;
                }}
                .content {{
                    background-color: white;
                    padding: 30px;
                    border: 1px solid #ddd;
                }}
                .cta-button {{
                    display: inline-block;
                    background-color: #c53030;
                    color: white;
                    padding: 12px 24px;
                    text-decoration: none;
                    margin: 20px 0;
                    font-weight: bold;
                    border-radius: 4px;
                }}
                .cta-button:hover {{
                    background-color: #9b2c2c;
                }}
                .secondary-button {{
                    display: inline-block;
                    background-color: #1a365d;
                    color: white;
                    padding: 12px 24px;
                    text-decoration: none;
                    margin: 20px 0;
                    font-weight: bold;
                    border-radius: 4px;
                }}
                .footer {{
                    text-align: center;
                    padding: 20px;
                    font-size: 12px;
                    color: #666;
                }}
                .footer a {{
                    color: #1a365d;
                }}
                .highlight-box {{
                    background-color: #f0f4f8;
                    border-left: 4px solid #1a365d;
                    padding: 15px;
                    margin: 20px 0;
                }}
                .warning-box {{
                    background-color: #fff5f5;
                    border-left: 4px solid #c53030;
                    padding: 15px;
                    margin: 20px 0;
                }}
                ul {{
                    padding-left: 20px;
                }}
                li {{
                    margin-bottom: 8px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>FEDERAL FRAUD WATCH</h1>
                <p style="margin: 5px 0 0 0; font-size: 14px;">Defending the Rule of Law</p>
            </div>
            <div class="content">
                {content}
            </div>
            <div class="footer">
                <p>Federal Fraud Watch | Exposing Waste, Fraud & Mismanagement</p>
                <p><a href="{self.SITE_URL}/unsubscribe">Unsubscribe</a> | <a href="{self.SITE_URL}/preferences">Update Preferences</a></p>
                <p>© {datetime.now().year} Federal Fraud Watch. All rights reserved.</p>
            </div>
        </body>
        </html>
        """

    def _generate_welcome_html(self, name: Optional[str], tier: str) -> str:
        greeting = f"Dear {name}," if name else "Welcome!"
        tier_benefits = self._get_tier_benefits(tier)
        benefits_html = "".join([f"<li>{b}</li>" for b in tier_benefits])

        content = f"""
        <p>{greeting}</p>
        <p>Thank you for joining Federal Fraud Watch. You're now part of a community dedicated to 
        government accountability and the rule of law.</p>
        
        <h3>Your {tier.title()} Membership Includes:</h3>
        <ul>{benefits_html}</ul>
        
        <p>We're committed to showing our work, linking to source documents, and admitting when 
        we're wrong. That's what sets us apart.</p>
        
        <a href="{self.SITE_URL}/articles" class="cta-button">Start Reading →</a>
        
        <p>If you have any questions, reply to this email or contact us at 
        <a href="mailto:{self.SUPPORT_EMAIL}">{self.SUPPORT_EMAIL}</a>.</p>
        
        <p>Thank you for your support,<br><strong>The Federal Fraud Watch Team</strong></p>
        """
        return self._base_template(content)

    def _generate_subscription_confirmation_html(self, name: Optional[str], tier: str, amount: int) -> str:
        greeting = f"Dear {name}," if name else "Hello!"
        amount_str = f"${amount / 100:.2f}"
        tier_benefits = self._get_tier_benefits(tier)
        benefits_html = "".join([f"<li>{b}</li>" for b in tier_benefits])

        content = f"""
        <p>{greeting}</p>
        <p>Your <strong>{tier.title()} Subscription</strong> is now active!</p>
        
        <div class="highlight-box">
            <strong>Subscription Details:</strong><br>
            Plan: {tier.title()}<br>
            Amount: {amount_str}/month
        </div>
        
        <h3>Your Benefits:</h3>
        <ul>{benefits_html}</ul>
        
        <a href="{self.SITE_URL}/articles" class="cta-button">Access Your Content →</a>
        
        <p>You can manage your subscription anytime from your 
        <a href="{self.SITE_URL}/account">account settings</a>.</p>
        
        <p>Thank you for supporting independent journalism,<br>
        <strong>The Federal Fraud Watch Team</strong></p>
        """
        return self._base_template(content)

    def _generate_upgrade_html(self, name: Optional[str], old_tier: str, new_tier: str) -> str:
        greeting = f"Dear {name}," if name else "Hello!"
        tier_benefits = self._get_tier_benefits(new_tier)
        benefits_html = "".join([f"<li>{b}</li>" for b in tier_benefits])

        content = f"""
        <p>{greeting}</p>
        <p>Congratulations! You've upgraded from <strong>{old_tier.title()}</strong> to 
        <strong>{new_tier.title()}</strong>!</p>
        
        <h3>Your New {new_tier.title()} Benefits:</h3>
        <ul>{benefits_html}</ul>
        
        <a href="{self.SITE_URL}/articles" class="cta-button">Explore Your New Access →</a>
        
        <p>Thank you for your continued support,<br>
        <strong>The Federal Fraud Watch Team</strong></p>
        """
        return self._base_template(content)

    def _generate_downgrade_html(self, name: Optional[str], old_tier: str, new_tier: str) -> str:
        greeting = f"Dear {name}," if name else "Hello!"
        
        content = f"""
        <p>{greeting}</p>
        <p>Your subscription has been updated from <strong>{old_tier.title()}</strong> to 
        <strong>{new_tier.title()}</strong>.</p>
        
        <p>Your new plan is now active. If you'd like to upgrade again at any time, you can 
        do so from your account settings.</p>
        
        <a href="{self.SITE_URL}/account" class="secondary-button">Manage Subscription →</a>
        
        <p>If this change was made in error, please contact us immediately at 
        <a href="mailto:{self.SUPPORT_EMAIL}">{self.SUPPORT_EMAIL}</a>.</p>
        
        <p>Best regards,<br>
        <strong>The Federal Fraud Watch Team</strong></p>
        """
        return self._base_template(content)

    def _generate_cancellation_html(self, name: Optional[str], tier: str, end_date: datetime) -> str:
        greeting = f"Dear {name}," if name else "Hello!"
        date_str = end_date.strftime("%B %d, %Y")
        
        content = f"""
        <p>{greeting}</p>
        <p>We're sorry to see you go. Your <strong>{tier.title()}</strong> subscription has been canceled.</p>
        
        <div class="highlight-box">
            <strong>Important:</strong> You'll continue to have access to your {tier.title()} benefits 
            until <strong>{date_str}</strong>.
        </div>
        
        <p>We'd love to know why you decided to cancel. Your feedback helps us improve. 
        Reply to this email or contact us at <a href="mailto:{self.SUPPORT_EMAIL}">{self.SUPPORT_EMAIL}</a>.</p>
        
        <p>If you change your mind, you can resubscribe anytime:</p>
        <a href="{self.SITE_URL}/subscribe" class="cta-button">Resubscribe →</a>
        
        <p>Thank you for being part of our community,<br>
        <strong>The Federal Fraud Watch Team</strong></p>
        """
        return self._base_template(content)

    def _generate_payment_failed_html(self, name: Optional[str], tier: str) -> str:
        greeting = f"Dear {name}," if name else "Hello!"
        
        content = f"""
        <p>{greeting}</p>
        
        <div class="warning-box">
            <strong>Action Required:</strong> We were unable to process your payment for your 
            {tier.title()} subscription.
        </div>
        
        <p>To avoid interruption to your service, please update your payment method as soon as possible.</p>
        
        <a href="{self.SITE_URL}/account/billing" class="cta-button">Update Payment Method →</a>
        
        <p>If you believe this is an error or need assistance, please contact us at 
        <a href="mailto:{self.SUPPORT_EMAIL}">{self.SUPPORT_EMAIL}</a>.</p>
        
        <p>Best regards,<br>
        <strong>The Federal Fraud Watch Team</strong></p>
        """
        return self._base_template(content)

    def _generate_receipt_html(self, name: Optional[str], tier: str, amount: int, invoice_id: str) -> str:
        greeting = f"Dear {name}," if name else "Hello!"
        amount_str = f"${amount / 100:.2f}"
        date_str = datetime.now().strftime("%B %d, %Y")
        
        content = f"""
        <p>{greeting}</p>
        <p>Thank you for your payment. Here's your receipt:</p>
        
        <div class="highlight-box">
            <strong>Payment Receipt</strong><br><br>
            Invoice ID: {invoice_id}<br>
            Date: {date_str}<br>
            Plan: {tier.title()} Subscription<br>
            Amount: {amount_str}<br>
            Status: <span style="color: green;">✓ Paid</span>
        </div>
        
        <p>This receipt serves as confirmation of your payment. For tax purposes, you may 
        want to save this email.</p>
        
        <p>Questions about your billing? Contact us at 
        <a href="mailto:{self.SUPPORT_EMAIL}">{self.SUPPORT_EMAIL}</a>.</p>
        
        <p>Thank you for your support,<br>
        <strong>The Federal Fraud Watch Team</strong></p>
        """
        return self._base_template(content)

    def _generate_support_confirmation_html(self, name: Optional[str], ticket_id: str, subject_line: str) -> str:
        greeting = f"Dear {name}," if name else "Hello!"
        
        content = f"""
        <p>{greeting}</p>
        <p>We've received your support request and will get back to you as soon as possible.</p>
        
        <div class="highlight-box">
            <strong>Ticket Details:</strong><br>
            Ticket ID: #{ticket_id}<br>
            Subject: {subject_line}<br>
            Status: Open
        </div>
        
        <p>Our typical response time is within 24-48 hours. For urgent matters, please 
        indicate "URGENT" in your reply.</p>
        
        <p>You can reply to this email to add more information to your ticket.</p>
        
        <p>Best regards,<br>
        <strong>Federal Fraud Watch Support</strong></p>
        """
        return self._base_template(content)

    def _generate_support_reply_html(self, name: Optional[str], ticket_id: str, reply_content: str) -> str:
        greeting = f"Dear {name}," if name else "Hello!"
        
        content = f"""
        <p>{greeting}</p>
        <p>We've responded to your support request:</p>
        
        <div class="highlight-box">
            <strong>Ticket #{ticket_id}</strong><br><br>
            {reply_content}
        </div>
        
        <p>If this resolves your issue, no further action is needed. Otherwise, simply reply 
        to this email to continue the conversation.</p>
        
        <p>Best regards,<br>
        <strong>Federal Fraud Watch Support</strong></p>
        """
        return self._base_template(content)

    def _generate_password_reset_html(self, name: Optional[str], reset_link: str) -> str:
        greeting = f"Dear {name}," if name else "Hello!"
        
        content = f"""
        <p>{greeting}</p>
        <p>We received a request to reset your password. Click the button below to create a new password:</p>
        
        <a href="{reset_link}" class="cta-button">Reset Password →</a>
        
        <p style="font-size: 14px; color: #666;">This link will expire in 1 hour.</p>
        
        <div class="warning-box">
            <strong>Didn't request this?</strong> If you didn't request a password reset, 
            please ignore this email or contact us if you're concerned about your account security.
        </div>
        
        <p>Best regards,<br>
        <strong>Federal Fraud Watch Support</strong></p>
        """
        return self._base_template(content)

    def _generate_email_verification_html(self, name: Optional[str], verification_link: str) -> str:
        greeting = f"Dear {name}," if name else "Hello!"
        
        content = f"""
        <p>{greeting}</p>
        <p>Please verify your email address by clicking the button below:</p>
        
        <a href="{verification_link}" class="cta-button">Verify Email →</a>
        
        <p style="font-size: 14px; color: #666;">This link will expire in 24 hours.</p>
        
        <p>If you didn't create an account with Federal Fraud Watch, please ignore this email.</p>
        
        <p>Best regards,<br>
        <strong>The Federal Fraud Watch Team</strong></p>
        """
        return self._base_template(content)

    def _generate_new_article_html(self, name: Optional[str], article_title: str, article_excerpt: str, article_url: str) -> str:
        greeting = f"Dear {name}," if name else "Hello!"
        
        content = f"""
        <p>{greeting}</p>
        <p>A new article has been published:</p>
        
        <h2 style="color: #1a365d;">{article_title}</h2>
        
        <p>{article_excerpt}</p>
        
        <a href="{article_url}" class="cta-button">Read Full Article →</a>
        
        <p>Thank you for being a subscriber,<br>
        <strong>The Federal Fraud Watch Team</strong></p>
        """
        return self._base_template(content)

    def _generate_trial_ending_html(self, name: Optional[str], days_left: int) -> str:
        greeting = f"Dear {name}," if name else "Hello!"
        day_word = "day" if days_left == 1 else "days"
        
        content = f"""
        <p>{greeting}</p>
        <p>Your free trial ends in <strong>{days_left} {day_word}</strong>.</p>
        
        <p>To continue enjoying full access to Federal Fraud Watch, subscribe now:</p>
        
        <a href="{self.SITE_URL}/subscribe" class="cta-button">Subscribe Now →</a>
        
        <h3>What You'll Get:</h3>
        <ul>
            <li>Full access to all articles and investigations</li>
            <li>Source document archive</li>
            <li>Exclusive newsletters</li>
            <li>And more...</li>
        </ul>
        
        <p>Questions? Reply to this email and we'll be happy to help.</p>
        
        <p>Best regards,<br>
        <strong>The Federal Fraud Watch Team</strong></p>
        """
        return self._base_template(content)

    def _get_tier_benefits(self, tier: str) -> List[str]:
        """Get benefits list for a subscription tier."""
        benefits = {
            "free": [
                "Weekly newsletter every Friday",
                "Access to free articles",
                "Social media content",
            ],
            "patriot": [
                "3x weekly newsletters (Mon/Wed/Fri)",
                "All articles with no paywall",
                "Access to source document archive",
                "Subscriber-only comment section",
            ],
            "watchdog": [
                "Everything in Patriot tier",
                "Weekly video analysis",
                "Monthly live Q&A sessions",
                "Early access to investigations (24hrs ahead)",
                "Private community access",
            ],
            "founder": [
                "Everything in Watchdog tier",
                "Quarterly virtual roundtable",
                "Direct messaging access",
                "Name in credits/acknowledgments",
                "Annual physical mailed report",
            ],
        }
        return benefits.get(tier.lower(), benefits["free"])

    def generate_newsletter_html(
        self,
        title: str,
        content: str,
        article_url: Optional[str] = None,
        unsubscribe_url: Optional[str] = None,
    ) -> str:
        """Generate HTML for newsletter email."""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title}</title>
            <style>
                body {{
                    font-family: Georgia, 'Times New Roman', serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f9f9f9;
                }}
                .header {{
                    background-color: #1a365d;
                    color: white;
                    padding: 20px;
                    text-align: center;
                    margin-bottom: 20px;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 24px;
                }}
                .content {{
                    background-color: white;
                    padding: 30px;
                    border: 1px solid #ddd;
                }}
                .article-title {{
                    color: #1a365d;
                    font-size: 22px;
                    margin-bottom: 15px;
                }}
                .cta-button {{
                    display: inline-block;
                    background-color: #c53030;
                    color: white;
                    padding: 12px 24px;
                    text-decoration: none;
                    margin: 20px 0;
                    font-weight: bold;
                }}
                .footer {{
                    text-align: center;
                    padding: 20px;
                    font-size: 12px;
                    color: #666;
                }}
                .footer a {{
                    color: #1a365d;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>FEDERAL FRAUD WATCH</h1>
                <p style="margin: 5px 0 0 0; font-size: 14px;">Defending the Rule of Law</p>
            </div>
            
            <div class="content">
                <h2 class="article-title">{title}</h2>
                
                {content}
                
                {f'<a href="{article_url}" class="cta-button">Read Full Article →</a>' if article_url else ''}
            </div>
            
            <div class="footer">
                <p>Federal Fraud Watch | Exposing Waste, Fraud & Mismanagement</p>
                {f'<p><a href="{unsubscribe_url}">Unsubscribe</a> | <a href="https://federalfraudwatch.com/preferences">Update Preferences</a></p>' if unsubscribe_url else ''}
                <p>© 2026 Federal Fraud Watch. All rights reserved.</p>
            </div>
        </body>
        </html>
        """

    def generate_welcome_email_html(self, name: Optional[str], tier: str) -> str:
        """Generate welcome email for new subscribers."""
        greeting = f"Dear {name}," if name else "Welcome!"
        
        tier_benefits = {
            "free": [
                "Weekly newsletter every Friday",
                "Access to free articles",
                "Social media content",
            ],
            "patriot": [
                "3x weekly newsletters (Mon/Wed/Fri)",
                "All articles with no paywall",
                "Access to source document archive",
                "Subscriber-only comment section",
            ],
            "watchdog": [
                "Everything in Patriot tier",
                "Weekly video analysis",
                "Monthly live Q&A sessions",
                "Early access to investigations (24hrs ahead)",
                "Private community access",
            ],
            "founder": [
                "Everything in Watchdog tier",
                "Quarterly virtual roundtable",
                "Direct messaging access",
                "Name in credits/acknowledgments",
                "Annual physical mailed report",
            ],
        }
        
        benefits = tier_benefits.get(tier, tier_benefits["free"])
        benefits_html = "".join([f"<li>{b}</li>" for b in benefits])
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Welcome to Federal Fraud Watch</title>
            <style>
                body {{
                    font-family: Georgia, 'Times New Roman', serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background-color: #1a365d;
                    color: white;
                    padding: 20px;
                    text-align: center;
                }}
                .content {{
                    padding: 30px;
                    background: white;
                    border: 1px solid #ddd;
                }}
                ul {{
                    padding-left: 20px;
                }}
                li {{
                    margin-bottom: 10px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>FEDERAL FRAUD WATCH</h1>
            </div>
            <div class="content">
                <p>{greeting}</p>
                
                <p>Thank you for subscribing to Federal Fraud Watch. You're now part of a 
                community dedicated to government accountability and the rule of law.</p>
                
                <h3>Your {tier.title()} Subscription Includes:</h3>
                <ul>
                    {benefits_html}
                </ul>
                
                <p>We're committed to showing our work, linking to source documents, and 
                admitting when we're wrong. That's what sets us apart.</p>
                
                <p>If you have any questions, reply to this email or contact us at 
                contact@federalfraudwatch.com.</p>
                
                <p>Thank you for your support,<br>
                <strong>The Federal Fraud Watch Team</strong></p>
            </div>
        </body>
        </html>
        """


email_service = EmailService()
