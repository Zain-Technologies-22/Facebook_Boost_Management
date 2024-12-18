from datetime import timedelta
import json
from pyexpat.errors import messages
from django.utils import timezone 
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from .models import Campaign, CampaignActivity
from django.core.paginator import Paginator
# Create your views here.

def create_campaign(request):
    if request.method == 'POST':
        try:
            campaign = Campaign.objects.create(
                name=request.POST.get('name'),
                campaign_type=request.POST.get('campaign_type'),
                description=request.POST.get('description'),
                start_date=request.POST.get('start_date'),
                end_date=request.POST.get('end_date'),
                budget=float(request.POST.get('budget', 0)),
                daily_budget=float(request.POST.get('daily_budget', 0)),
                target_audience=request.POST.get('target_audience'),
                platform=request.POST.get('platform'),
                auto_renewal=request.POST.get('auto_renewal') == 'on',
                user=request.user
            )
            messages.success(request, 'Campaign created successfully!')
            return redirect('campaign_detail', campaign.id)
        except Exception as e:
            messages.error(request, f'Error creating campaign: {str(e)}')
            return redirect('campaigns')
    
    return redirect('campaigns')


@login_required
def campaigns(request):
    # Get all campaigns for the current user
    all_campaigns = Campaign.objects.filter(user=request.user).order_by('-start_date')
    
    # Handle filters
    status = request.GET.get('status')
    campaign_type = request.GET.get('type')
    search = request.GET.get('search')
    
    if status:
        all_campaigns = all_campaigns.filter(status=status)
    if campaign_type:
        all_campaigns = all_campaigns.filter(type=campaign_type)
    if search:
        all_campaigns = all_campaigns.filter(name__icontains=search)
    
    # Pagination
    paginator = Paginator(all_campaigns, 9)  # Show 9 campaigns per page
    page = request.GET.get('page')
    campaigns = paginator.get_page(page)
    
    context = {
        'campaigns': campaigns,
    }
    return render(request, 'campaigns/campaigns.html', context)


@login_required
def campaign_detail(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id, user=request.user)
    
    # Get recent activities
    recent_activities = CampaignActivity.objects.filter(
        campaign=campaign
    ).order_by('-timestamp')[:5]
    
    # Generate sample data for the performance chart
    dates = []
    followers_data = []
    engagement_data = []
    
    current_date = campaign.start_date
    while current_date <= min(timezone.now().date(), campaign.end_date):
        dates.append(current_date.strftime("%Y-%m-%d"))
        followers_data.append(campaign.followers_gained * (current_date - campaign.start_date).days // campaign.duration)
        engagement_data.append(round(campaign.likes_count / max(1, campaign.followers_gained) * 100, 2))
        current_date += timedelta(days=1)

    context = {
        'campaign': campaign,
        'chart_labels': json.dumps(dates),
        'followers_data': json.dumps(followers_data),
        'engagement_data': json.dumps(engagement_data),
    }
    
    
    return render(request, 'campaigns/campaign_detail.html', context)


@login_required
def edit_campaign(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id, user=request.user)
    
    if request.method == 'POST':
        # Handle form submission
        campaign.name = request.POST.get('name')
        campaign.description = request.POST.get('description')
        campaign.target_audience = request.POST.get('target_audience')
        campaign.daily_budget = request.POST.get('daily_budget')
        campaign.save()
        
        return redirect('campaign_detail', campaign_id=campaign.id)
    
    return render(request, 'campaigns/edit_campaign.html', {'campaign': campaign})