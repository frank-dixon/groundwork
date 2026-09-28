from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Prefetch
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.decorators.http import require_http_methods, require_POST
from pathlib import Path

from django.conf import settings

from .forms import BedForm, LayoutForm, PlacementForm, PlotForm, RegisterForm, SuggestForm
from .models import Bed, Layout, Plant, PlantPlacement, Plot
from .suggest import all_layout_citations, suggest_fill_with_plan


class GroundworkLoginView(LoginView):
    template_name = 'registration/login.html'
    redirect_authenticated_user = True


class GroundworkLogoutView(LogoutView):
    next_page = reverse_lazy('home')


def register(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Welcome to Groundwork. Let’s set up your plot.')
            return redirect('onboarding')
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})


def home(request):
    if request.user.is_authenticated:
        layouts = Layout.objects.filter(user=request.user).select_related('plot')
        if not layouts.exists():
            return redirect('onboarding')
        return render(request, 'garden/home.html', {'layouts': layouts})
    return render(request, 'garden/landing.html')


@login_required
def onboarding(request):
    """First-run plot onboarding when the user has no layouts."""
    has_layouts = Layout.objects.filter(user=request.user).exists()
    if has_layouts and request.method == 'GET' and request.GET.get('force') != '1':
        return redirect('home')

    if request.method == 'POST':
        form = PlotForm(request.POST)
        if form.is_valid():
            plot = form.save(commit=False)
            plot.user = request.user
            plot.save()
            layout = Layout.objects.create(
                user=request.user,
                plot=plot,
                name=f'{plot.name} layout',
            )
            # Default bed spanning most of the plot with a small margin
            Bed.objects.create(
                layout=layout,
                name='Main bed',
                x_ft=0.5,
                y_ft=0.5,
                width_ft=max(float(plot.width_ft) - 1, 1),
                length_ft=max(float(plot.length_ft) - 1, 1),
            )
            messages.success(request, f'Plot “{plot.name}” created. Add plants or try Suggest.')
            return redirect(layout.get_absolute_url())
    else:
        form = PlotForm(initial={'name': 'My garden', 'width_ft': 10, 'length_ft': 12})
    return render(request, 'garden/onboarding.html', {'form': form, 'has_layouts': has_layouts})


@login_required
def layout_list(request):
    layouts = Layout.objects.filter(user=request.user).select_related('plot')
    return render(request, 'garden/layout_list.html', {'layouts': layouts})


@login_required
def layout_create(request):
    if request.method == 'POST':
        form = LayoutForm(request.POST, user=request.user)
        if form.is_valid():
            layout = form.save(commit=False)
            layout.user = request.user
            layout.save()
            messages.success(request, f'Layout “{layout.name}” created.')
            return redirect(layout.get_absolute_url())
    else:
        form = LayoutForm(user=request.user)
    return render(request, 'garden/layout_form.html', {'form': form, 'title': 'New layout'})


@login_required
def layout_detail(request, pk):
    layout = get_object_or_404(
        Layout.objects.filter(user=request.user)
        .select_related('plot')
        .prefetch_related(
            Prefetch(
                'beds',
                queryset=Bed.objects.prefetch_related('placements__plant'),
            )
        ),
        pk=pk,
    )
    bed_form = BedForm()
    suggest_form = SuggestForm()
    return render(
        request,
        'garden/layout_detail.html',
        {
            'layout': layout,
            'bed_form': bed_form,
            'suggest_form': suggest_form,
            'layout_citations': all_layout_citations(),
            'suggest_plan': request.session.pop('suggest_plan', None),
        },
    )


@login_required
def layout_edit(request, pk):
    layout = get_object_or_404(Layout, pk=pk, user=request.user)
    if request.method == 'POST':
        form = LayoutForm(request.POST, instance=layout, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Layout updated.')
            return redirect(layout.get_absolute_url())
    else:
        form = LayoutForm(instance=layout, user=request.user)
    return render(request, 'garden/layout_form.html', {'form': form, 'title': 'Edit layout', 'layout': layout})


@login_required
@require_POST
def layout_delete(request, pk):
    layout = get_object_or_404(Layout, pk=pk, user=request.user)
    name = layout.name
    layout.delete()
    messages.info(request, f'Layout “{name}” deleted.')
    if not Layout.objects.filter(user=request.user).exists():
        return redirect('onboarding')
    return redirect('layout_list')


@login_required
@require_POST
def bed_create(request, layout_pk):
    layout = get_object_or_404(Layout, pk=layout_pk, user=request.user)
    form = BedForm(request.POST)
    if form.is_valid():
        bed = form.save(commit=False)
        bed.layout = layout
        bed.save()
        messages.success(request, f'Bed “{bed.name}” added.')
    else:
        messages.error(request, 'Could not add bed. Check the form.')
    return redirect(layout.get_absolute_url())


@login_required
@require_POST
def bed_delete(request, pk):
    bed = get_object_or_404(Bed, pk=pk, layout__user=request.user)
    layout = bed.layout
    bed.delete()
    messages.info(request, 'Bed removed.')
    return redirect(layout.get_absolute_url())


@login_required
def placement_add(request, bed_pk):
    bed = get_object_or_404(Bed, pk=bed_pk, layout__user=request.user)
    if request.method == 'POST':
        form = PlacementForm(request.POST)
        if form.is_valid():
            placement = form.save(commit=False)
            placement.bed = bed
            placement.save()
            messages.success(request, f'Added {placement.plant.name}.')
            return redirect(bed.layout.get_absolute_url())
    else:
        form = PlacementForm()
    return render(request, 'garden/placement_form.html', {'form': form, 'bed': bed})


@login_required
@require_POST
def placement_delete(request, pk):
    placement = get_object_or_404(PlantPlacement, pk=pk, bed__layout__user=request.user)
    layout = placement.bed.layout
    placement.delete()
    messages.info(request, 'Placement removed.')
    return redirect(layout.get_absolute_url())


@login_required
@require_POST
def layout_suggest(request, pk):
    layout = get_object_or_404(Layout, pk=pk, user=request.user)
    form = SuggestForm(request.POST)
    if not form.is_valid():
        messages.error(request, 'Pick at least one plant to suggest.')
        return redirect(layout.get_absolute_url())
    plants = list(form.cleaned_data['plants'])
    beds = list(layout.beds.all())
    if not beds:
        messages.error(request, 'Add a bed before suggesting a layout.')
        return redirect(layout.get_absolute_url())
    total = 0
    last_plan = None
    for bed in beds:
        result = suggest_fill_with_plan(bed, plants, clear=True)
        total += len(result.placements)
        last_plan = result.plan
    tmpl_names = [t['name'] for t in (last_plan.templates_used if last_plan else [])]
    why = '; '.join(tmpl_names) if tmpl_names else 'per-crop spacing blocks'
    messages.success(
        request,
        f'Suggested {total} placement(s) across {len(beds)} bed(s) using intentional templates: {why}.',
    )
    if last_plan:
        request.session['suggest_plan'] = {
            'summary': last_plan.summary,
            'templates_used': last_plan.templates_used,
            'succession_notes': last_plan.succession_notes,
            'citations': last_plan.citations,
        }
    return redirect(layout.get_absolute_url())


def plant_list(request):
    plants = Plant.objects.all()
    return render(request, 'garden/plant_list.html', {'plants': plants})


def plant_detail(request, slug):
    plant = get_object_or_404(
        Plant.objects.prefetch_related('companions', 'antagonists'),
        slug=slug,
    )
    return render(request, 'garden/plant_detail.html', {'plant': plant})


@login_required
def pro_stub(request):
    """Stripe Pro stub — no real billing yet."""
    return render(request, 'garden/pro.html')


def service_worker(request):
    path = Path(settings.BASE_DIR) / 'static' / 'sw.js'
    if not path.exists():
        raise Http404
    return FileResponse(path.open('rb'), content_type='application/javascript')


def manifest(request):
    path = Path(settings.BASE_DIR) / 'static' / 'manifest.webmanifest'
    if not path.exists():
        raise Http404
    return FileResponse(path.open('rb'), content_type='application/manifest+json')
