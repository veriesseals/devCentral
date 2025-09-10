import markdown

def render_markdown(text: str) -> str:
    return markdown.markdown(
        text or "",
        extensions=['fenced_code', 'codehilite'],
        output_format='html5'
    )

def render_markdown(text: str) -> str:
    return markdown.markdown(
        text or "",
        extensions=['fenced_code', 'codehilite'],
        output_format='html5'
    )
    
from .utils import render_markdown
def profile_view(request, username):
    # ... existing code to find profile_user, posts, etc.
    posts = Post.objects.filter(author=profile_user).order_by('-created_at')

    for p in posts:
        p.rendered_html = render_markdown(p.body)

    return render(request, 'profile.html', {
        'profile_user': profile_user,
        'posts': posts,
        # ... other context
    })