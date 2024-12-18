from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from .forms import SignUpForm


def index_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'index.html')

@login_required
def dashboard_view(request):
    return render(request, 'dashboard/dashboard.html')


@login_required
def credits(request):
    return render(request, 'dashboard/credits.html')

@login_required
def analytics(request):
    # Followers calculations
    current_followers = 1000  # Get from your database
    previous_followers = 900  # Get previous period data
    
    # Engagement calculations
    current_engagement_growth = 1000  # Get from your database
    previous_engagement_growth = 1000  # Get previous period data
    
    # Likes calculations
    current_likes = 500  # Get from your database
    previous_likes = 400  # Get previous period data
    
    # Comments calculations
    current_comments = 300  # Get from your database
    previous_comments = 250  # Get previous period data
    
    # Calculate growth percentages
    if previous_followers > 0:
        followers_growth = ((current_followers - previous_followers) / previous_followers) * 100
        engagement_growth = ((current_engagement_growth - previous_engagement_growth) / previous_engagement_growth) * 100
        likes_growth = ((current_likes - previous_likes) / previous_likes) * 100
        comments_growth = ((current_comments - previous_comments) / previous_comments) * 100
    else:
        followers_growth = 0
        engagement_growth = 0
        likes_growth = 0
        comments_growth = 0

    # Example detailed stats data
    detailed_stats = [
        {
            'date': '2024-01-01',
            'followers': 1000,
            'engagement': 5.2,
            'likes': 500,
            'comments': 300,
            'shares': 100,
            'growth': 2.5
        },
        # Add more entries as needed
    ]
    
    context = {
        # Growth metrics
        'followers_growth': followers_growth,
        'followers_growth_abs': abs(followers_growth),
        'engagement_growth': engagement_growth,
        'engagement_growth_abs': abs(engagement_growth),
        'likes_growth': likes_growth,
        'likes_growth_abs': abs(likes_growth),
        'comments_growth': comments_growth,
        'comments_growth_abs': abs(comments_growth),
        
        # Total metrics
        'total_likes': current_likes,
        'total_comments': current_comments,
        
        # Detailed stats
        'detailed_stats': detailed_stats,
    }
    
    return render(request, 'dashboard/analytics.html', context)